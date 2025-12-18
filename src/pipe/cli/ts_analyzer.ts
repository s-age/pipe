/* eslint-disable no-console */
import fs from "fs";
import path from "path";
import { dirname } from "path";
import { fileURLToPath } from "url";

import {
  Project,
  SyntaxKind,
  PropertyDeclaration,
  MethodDeclaration,
  ParameterDeclaration,
  SourceFile,
  Identifier,
  Node,
  Symbol,
  PropertySignature,
  ArrowFunction,
} from "ts-morph";

type ReferenceEntry = {
  filePath: string;
  line?: number;
  lineNumber?: number;
  column: number;
  snippet: string;
};

type TypeDefinition = {
  type?: string;
  properties?: any[];
  methods?: any[];
  parameters?: any[];
  returnType?: string;
  propsType?: string;
  props?: any[];
  variableType?: string;
  definition?: string;
};

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = path.join(__dirname, "..", "..", "..");

const getTypeDefinitions = (filePath: string, symbolName: string, project: Project): TypeDefinition | null => {
  const sourceFile = project.addSourceFileAtPath(filePath);
  const definitions: TypeDefinition = {};

  // Find class declarations
  const classDeclaration = sourceFile.getClass(symbolName);
  if (classDeclaration) {
    definitions.type = "class";
    definitions.properties = classDeclaration.getProperties().map((p: PropertyDeclaration) => ({
      name: p.getName(),
      type: p.getType().getText(),
      isStatic: p.isStatic(),
      isReadonly: p.isReadonly(),
    }));
    definitions.methods = classDeclaration.getMethods().map((m: MethodDeclaration) => ({
      name: m.getName(),
      parameters: m.getParameters().map((p: ParameterDeclaration) => ({
        name: p.getName(),
        type: p.getType().getText(),
      })),
      returnType: m.getReturnType().getText(),
      isStatic: m.isStatic(),
    }));

    return definitions;
  }

  // Find function declarations
  const functionDeclaration = sourceFile.getFunction(symbolName);
  if (functionDeclaration) {
    definitions.type = "function";
    definitions.parameters = functionDeclaration.getParameters().map((p: ParameterDeclaration) => ({
      name: p.getName(),
      type: p.getType().getText(),
    }));
    definitions.returnType = functionDeclaration.getReturnType().getText();

    return definitions;
  }

  // Find variable declarations (const, let, var)
  const variableDeclaration = sourceFile.getVariableDeclaration(symbolName);
  if (variableDeclaration) {
    const initializer = variableDeclaration.getInitializer();

    // Check if it's an arrow function component
    if (initializer && initializer.getKind() === SyntaxKind.ArrowFunction) {
      const arrowFunction = initializer as ArrowFunction;
      const parameters = arrowFunction.getParameters();
      const returnType = arrowFunction.getReturnType().getText();

      if (parameters.length > 0) {
        const firstParameter = parameters[0];
        const firstParameterType = firstParameter.getTypeNode();

        if (firstParameterType && firstParameterType.getKind() === SyntaxKind.TypeReference) {
          const propertiesTypeName = firstParameterType.getText();
          const propertiesInterface = sourceFile.getInterface(propertiesTypeName);
          const propertiesTypeAlias = sourceFile.getTypeAlias(propertiesTypeName);

          if (propertiesInterface) {
            definitions.type = "React.ArrowFunctionComponent";
            definitions.propsType = propertiesTypeName;
            definitions.returnType = returnType;
            definitions.props = propertiesInterface.getProperties().map((p: PropertySignature) => ({
              name: p.getName(),
              type: p.getType().getText(),
              isOptional: p.hasQuestionToken(),
            }));

            return definitions;
          } else if (propertiesTypeAlias) {
            definitions.type = "React.ArrowFunctionComponent";
            definitions.propsType = propertiesTypeName;
            definitions.returnType = returnType;
            const aliasedType = propertiesTypeAlias.getType();
            const properties = aliasedType.getProperties();
            if (properties) {
              definitions.props = properties.map((p: Symbol) => ({
                name: p.getName(),
                type: p.getTypeAtLocation(propertiesTypeAlias).getText(),
                isOptional: p.isOptional(),
              }));
            } else {
              definitions.props = [];
            }

            return definitions;
          }
        }
      }
      // If no specific Props type is found but it's an arrow function
      definitions.type = "React.ArrowFunctionComponent";
      definitions.parameters = parameters.map((p: ParameterDeclaration) => ({
        name: p.getName(),
        type: p.getType().getText(),
      }));
      definitions.returnType = returnType;

      return definitions;
    }

    definitions.type = "variable";
    definitions.variableType = variableDeclaration.getType().getText();

    return definitions;
  }

  // Find interfaces
  const interfaceDeclaration = sourceFile.getInterface(symbolName);
  if (interfaceDeclaration) {
    definitions.type = "interface";
    definitions.properties = interfaceDeclaration.getProperties().map((p: PropertySignature) => ({
      name: p.getName(),
      type: p.getType().getText(),
    }));

    return definitions;
  }

  // Find type aliases
  const typeAliasDeclaration = sourceFile.getTypeAlias(symbolName);
  if (typeAliasDeclaration) {
    definitions.type = "typeAlias";
    definitions.definition = typeAliasDeclaration.getTypeNode()!.getText();

    return definitions;
  }

  return null;
};

const getReferences = (filePath: string, symbolName: string, project: Project): ReferenceEntry[] => {
  const references: ReferenceEntry[] = [];

  const symbol = project
    .getSourceFiles()
    .flatMap((sf: SourceFile) => sf.getDescendantsOfKind(SyntaxKind.Identifier))
    .find((id: Identifier) => id.getText() === symbolName);

  if (symbol) {
    const symbolReferences = symbol.findReferencesAsNodes();
    symbolReferences.forEach((reference: Node) => {
      const start = reference.getStart();
      const sourceFile = reference.getSourceFile();
      const lineAndColumn = sourceFile.getLineAndColumnAtPos(start);
      references.push({
        filePath: sourceFile.getFilePath(),
        lineNumber: lineAndColumn.line,
        column: lineAndColumn.column,
        snippet: sourceFile.getFullText().split("\n")[lineAndColumn.line - 1].trim(),
      });
    });
  }

  return references;
};

const getCodeSnippet = (filePath: string, symbolName: string, project: Project): string | null => {
  const sourceFile = project.addSourceFileAtPath(filePath);

  // Try to find a class, function, variable, interface, or type alias
  const declaration =
    sourceFile.getClass(symbolName) ||
    sourceFile.getFunction(symbolName) ||
    sourceFile.getInterface(symbolName) ||
    sourceFile.getTypeAlias(symbolName);

  if (declaration) {
    return declaration.getText();
  }

  // Try to find a top-level variable declaration
  const topLevelVariableDecl = sourceFile.getVariableDeclaration(symbolName);
  if (topLevelVariableDecl) {
    const initializer = topLevelVariableDecl.getInitializer();
    if (initializer && initializer.getKind() === SyntaxKind.ArrowFunction) {
      // For arrow function components, return the entire variable statement
      return topLevelVariableDecl.getParent().getText();
    }
    // Handle useCallback, useMemo, etc.
    if (initializer && initializer.getKind() === SyntaxKind.CallExpression) {
      return topLevelVariableDecl.getText();
    }

    return topLevelVariableDecl.getText();
  }

  // Search all variable declarations (including nested ones)
  const allVariableDeclarations = sourceFile.getDescendantsOfKind(SyntaxKind.VariableDeclaration);
  for (const variableDecl of allVariableDeclarations) {
    if (variableDecl.getName() === symbolName) {
      return variableDecl.getText();
    }
  }

  // Search for the symbol in all identifiers (for properties, object literals, etc.)
  const allIdentifiers = sourceFile.getDescendantsOfKind(SyntaxKind.Identifier);
  for (const identifier of allIdentifiers) {
    if (identifier.getText() === symbolName) {
      // Check if it's a property assignment or object literal property
      const parent = identifier.getParent();
      if (parent) {
        const parentKind = parent.getKind();
        if (
          parentKind === SyntaxKind.PropertyAssignment ||
          parentKind === SyntaxKind.PropertyDeclaration ||
          parentKind === SyntaxKind.MethodDeclaration
        ) {
          return parent.getText();
        }
      }
    }
  }

  // If not found by name, check for default export if the symbol name matches the file name
  const fileNameWithoutExtension = path.parse(filePath).name;
  if (symbolName === fileNameWithoutExtension) {
    const defaultExportSymbol = sourceFile.getDefaultExportSymbol();
    if (defaultExportSymbol) {
      const declarations = defaultExportSymbol.getDeclarations();
      for (const decl of declarations) {
        if (decl.getKind() === SyntaxKind.VariableDeclaration || decl.getKind() === SyntaxKind.VariableStatement) {
          return decl.getText();
        }
      }
    }
  }

  return null;
};

const getFileContentSnippet = (filePath: string): string | null => {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return null;
  }
};

const getSnippetAndTypeDefinitions = (
  filePath: string,
  symbolName: string,
  project: Project
): { snippet: string | null; typeDefinitions: TypeDefinition | null } => {
  const snippet = getCodeSnippet(filePath, symbolName, project);
  const typeDefinitions = getTypeDefinitions(filePath, symbolName, project);

  return { snippet, typeDefinitions };
};

const calculateSimilarity = (string1: string, string2: string): number => {
  const m = string1.length;
  const n = string2.length;
  const dp = Array(m + 1)
    .fill(0)
    .map(() => Array(n + 1).fill(0));

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (string1[i - 1] === string2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }
  const lcs = dp[m][n];

  return (2 * lcs) / (m + n);
};

const getExportedSymbols = (filePath: string, project: Project): string[] => {
  const sourceFile = project.addSourceFileAtPath(filePath);
  const exportedDeclarations = sourceFile.getExportedDeclarations();
  const symbols: string[] = [];

  for (const [name] of exportedDeclarations) {
    symbols.push(name);
  }

  return symbols;
};

const findSimilarCode = (
  baseFilePath: string,
  symbolName: string,
  searchDirectory: string,
  maxResults: number = 3,
  project: Project
): ReferenceEntry[] => {
  const baseInfo = getSnippetAndTypeDefinitions(baseFilePath, symbolName, project);
  if (!baseInfo.snippet) {
    console.error(`DEBUG: No base snippet found for symbol '${symbolName}' in ${baseFilePath}`);

    return [];
  }

  const baseSnippet = baseInfo.snippet;

  const tsFiles: string[] = [];
  const walkSync = (currentDirectory: string): void => {
    const files = fs.readdirSync(currentDirectory);
    for (const file of files) {
      const fullPath = path.join(currentDirectory, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        if (file !== "node_modules") {
          walkSync(fullPath);
        }
      } else if ((file.endsWith(".ts") || file.endsWith(".tsx")) && !file.endsWith(".css.ts")) {
        process.stderr.write(`DEBUG: Found TS/TSX file: ${fullPath}\n`);
        tsFiles.push(fullPath);
      } else {
        process.stderr.write(`DEBUG: Skipping non-TS/TSX or .css.ts file: ${fullPath}\n`);
      }
    }
  };
  walkSync(searchDirectory);
  process.stderr.write(`DEBUG: Total TS/TSX files found: ${tsFiles.length}\n`);

  const similarCodes: any[] = [];

  for (const filePath of tsFiles) {
    if (path.resolve(filePath) === path.resolve(baseFilePath)) {
      process.stderr.write(`DEBUG: Skipping base file: ${filePath}\n`);
      continue;
    }

    const exportedSymbols = getExportedSymbols(filePath, project);
    process.stderr.write(`DEBUG: Exported symbols in ${filePath}: ${exportedSymbols.join(", ")}\n`);

    for (const targetSymbol of exportedSymbols) {
      const otherSnippet = getCodeSnippet(filePath, targetSymbol, project);
      if (otherSnippet) {
        const similarity = calculateSimilarity(baseSnippet, otherSnippet);
        process.stderr.write(
          `DEBUG: Comparing ${symbolName} (base) with ${targetSymbol} (${filePath}). Similarity: ${similarity}\n`
        );
        if (similarity > 0.5) {
          // 類似度の閾値
          process.stderr.write(`DEBUG: Found similar code (similarity > 0.5): ${targetSymbol} in ${filePath}\n`);
          similarCodes.push({
            filePath: filePath,
            symbolName: targetSymbol,
            similarity: similarity,
            snippet: otherSnippet,
          });
        } else {
          process.stderr.write(`DEBUG: Similarity below threshold (0.5): ${targetSymbol} in ${filePath}\n`);
        }
      } else {
        process.stderr.write(`DEBUG: No snippet found for symbol '${targetSymbol}' in ${filePath}\n`);
      }
    }
  }

  similarCodes.sort((a, b) => b.similarity - a.similarity);

  return similarCodes.slice(0, maxResults);
};

const analyzeFile = (filePath: string, project: Project): any => {
  const sourceFile = project.addSourceFileAtPath(filePath);
  const result: any = {
    file_path: filePath,
    imports: [],
    exports: [],
    classes: [],
    interfaces: [],
    type_aliases: [],
    functions: [],
    variables: [],
  };

  // Extract imports
  sourceFile.getImportDeclarations().forEach((importDecl) => {
    const moduleSpecifier = importDecl.getModuleSpecifierValue();
    const namedImports = importDecl.getNamedImports().map((ni) => ni.getName());
    const defaultImport = importDecl.getDefaultImport()?.getText();
    const namespaceImport = importDecl.getNamespaceImport()?.getText();

    result.imports.push({
      module: moduleSpecifier,
      named_imports: namedImports,
      default_import: defaultImport || null,
      namespace_import: namespaceImport || null,
      lineno: importDecl.getStartLineNumber(),
    });
  });

  // Extract exports
  sourceFile.getExportDeclarations().forEach((exportDecl) => {
    const moduleSpecifier = exportDecl.getModuleSpecifierValue();
    const namedExports = exportDecl.getNamedExports().map((ne) => ne.getName());

    result.exports.push({
      module: moduleSpecifier || null,
      named_exports: namedExports,
      lineno: exportDecl.getStartLineNumber(),
      is_re_export: !!moduleSpecifier,
    });
  });

  // Extract classes
  sourceFile.getClasses().forEach((cls) => {
    const classInfo: any = {
      name: cls.getName(),
      lineno: cls.getStartLineNumber(),
      end_lineno: cls.getEndLineNumber(),
      is_exported: cls.isExported(),
      is_default_export: cls.isDefaultExport(),
      base_classes: cls.getBaseTypes().map((t) => t.getText()),
      properties: [],
      methods: [],
    };

    // Extract properties
    cls.getProperties().forEach((prop: PropertyDeclaration) => {
      classInfo.properties.push({
        name: prop.getName(),
        lineno: prop.getStartLineNumber(),
        end_lineno: prop.getEndLineNumber(),
        type_hint: prop.getType().getText(),
        is_static: prop.isStatic(),
        is_readonly: prop.isReadonly(),
        is_optional: prop.hasQuestionToken(),
      });
    });

    // Extract methods
    cls.getMethods().forEach((method: MethodDeclaration) => {
      const parameters = method.getParameters().map((p: ParameterDeclaration) => ({
        name: p.getName(),
        type: p.getType().getText(),
        is_optional: p.hasQuestionToken(),
      }));

      classInfo.methods.push({
        name: method.getName(),
        lineno: method.getStartLineNumber(),
        end_lineno: method.getEndLineNumber(),
        signature: method.getText().split("{")[0].trim(),
        parameters: parameters.map((p) => `${p.name}${p.is_optional ? "?" : ""}: ${p.type}`),
        return_type: method.getReturnType().getText(),
        is_static: method.isStatic(),
        is_async: method.isAsync(),
      });
    });

    result.classes.push(classInfo);
  });

  // Extract interfaces
  sourceFile.getInterfaces().forEach((iface) => {
    const interfaceInfo: any = {
      name: iface.getName(),
      lineno: iface.getStartLineNumber(),
      end_lineno: iface.getEndLineNumber(),
      is_exported: iface.isExported(),
      is_default_export: iface.isDefaultExport(),
      properties: [],
      extends: iface.getExtends().map((e) => e.getText()),
    };

    iface.getProperties().forEach((prop: PropertySignature) => {
      interfaceInfo.properties.push({
        name: prop.getName(),
        lineno: prop.getStartLineNumber(),
        end_lineno: prop.getEndLineNumber(),
        type_hint: prop.getType().getText(),
        is_optional: prop.hasQuestionToken(),
      });
    });

    result.interfaces.push(interfaceInfo);
  });

  // Extract type aliases
  sourceFile.getTypeAliases().forEach((typeAlias) => {
    result.type_aliases.push({
      name: typeAlias.getName(),
      lineno: typeAlias.getStartLineNumber(),
      end_lineno: typeAlias.getEndLineNumber(),
      is_exported: typeAlias.isExported(),
      is_default_export: typeAlias.isDefaultExport(),
      definition: typeAlias.getTypeNode()?.getText() || "",
    });
  });

  // Extract functions
  sourceFile.getFunctions().forEach((func) => {
    const parameters = func.getParameters().map((p: ParameterDeclaration) => ({
      name: p.getName(),
      type: p.getType().getText(),
      is_optional: p.hasQuestionToken(),
    }));

    result.functions.push({
      name: func.getName(),
      lineno: func.getStartLineNumber(),
      end_lineno: func.getEndLineNumber(),
      is_exported: func.isExported(),
      is_default_export: func.isDefaultExport(),
      signature: func.getText().split("{")[0].trim(),
      parameters: parameters.map((p) => `${p.name}${p.is_optional ? "?" : ""}: ${p.type}`),
      return_type: func.getReturnType().getText(),
      is_async: func.isAsync(),
    });
  });

  // Extract top-level variables (including arrow functions)
  sourceFile.getVariableDeclarations().forEach((varDecl) => {
    const initializer = varDecl.getInitializer();
    const variableStatement = varDecl.getVariableStatement();

    // Get declaration type (const, let, var)
    const declarationKind = variableStatement?.getDeclarationKind() || "unknown";

    const varInfo: any = {
      name: varDecl.getName(),
      lineno: varDecl.getStartLineNumber(),
      end_lineno: varDecl.getEndLineNumber(),
      type_hint: varDecl.getType().getText(),
      is_exported: variableStatement?.isExported() || false,
      declaration_type: declarationKind, // const, let, or var
    };

    // Check if it's an arrow function
    if (initializer && initializer.getKind() === SyntaxKind.ArrowFunction) {
      const arrowFunc = initializer as ArrowFunction;
      const parameters = arrowFunc.getParameters().map((p: ParameterDeclaration) => ({
        name: p.getName(),
        type: p.getType().getText(),
        is_optional: p.hasQuestionToken(),
      }));

      varInfo.is_arrow_function = true;
      varInfo.parameters = parameters.map((p) => `${p.name}${p.is_optional ? "?" : ""}: ${p.type}`);
      varInfo.return_type = arrowFunc.getReturnType().getText();
    }

    result.variables.push(varInfo);
  });

  return result;
};

const buildDependencyTree = (
  filePath: string,
  project: Project,
  maxDepth: number = 3,
  visited: Set<string> = new Set()
): any => {
  const absPath = path.resolve(filePath);

  // Circular dependency detection
  if (visited.has(absPath)) {
    return {
      file_path: filePath,
      circular: true,
    };
  }

  visited.add(absPath);

  const sourceFile = project.addSourceFileAtPath(absPath);
  const result: any = {
    file_path: filePath,
    components: [],
    hooks: [],
    actions: [],
    types: [],
    utils: [],
    circular: false,
  };

  if (maxDepth === 0) {
    result.max_depth_reached = true;
    return result;
  }

  // Extract JSX elements (components used)
  const jsxElements = sourceFile.getDescendantsOfKind(SyntaxKind.JsxOpeningElement);
  const jsxSelfClosing = sourceFile.getDescendantsOfKind(SyntaxKind.JsxSelfClosingElement);

  const componentNames = new Set<string>();
  [...jsxElements, ...jsxSelfClosing].forEach((element) => {
    const tagName = element.getTagNameNode().getText();
    // Skip HTML elements (lowercase)
    if (tagName[0] === tagName[0].toUpperCase()) {
      componentNames.add(tagName);
    }
  });

  // Map component names to their import sources
  const imports = sourceFile.getImportDeclarations();
  const importMap = new Map<string, string>();

  imports.forEach((importDecl) => {
    const moduleSpecifier = importDecl.getModuleSpecifierValue();
    const defaultImport = importDecl.getDefaultImport()?.getText();
    const namedImports = importDecl.getNamedImports().map((ni) => ni.getName());

    if (defaultImport) {
      importMap.set(defaultImport, moduleSpecifier);
    }
    namedImports.forEach((name) => {
      importMap.set(name, moduleSpecifier);
    });
  });

  // Resolve component dependencies
  componentNames.forEach((compName) => {
    const source = importMap.get(compName);
    if (source && !source.startsWith("react")) {
      const resolvedPath = resolveModulePath(absPath, source);
      if (resolvedPath) {
        const childTree = buildDependencyTree(resolvedPath, project, maxDepth - 1, new Set(visited));
        result.components.push({
          name: compName,
          source: source,
          dependencies: childTree,
        });
      } else {
        result.components.push({
          name: compName,
          source: source,
          dependencies: null,
        });
      }
    }
  });

  // Extract hook calls (use* pattern)
  const callExpressions = sourceFile.getDescendantsOfKind(SyntaxKind.CallExpression);
  const hookCalls = new Set<string>();

  callExpressions.forEach((call) => {
    const expression = call.getExpression();
    const text = expression.getText();
    if (text.startsWith("use") && text[3] === text[3].toUpperCase()) {
      hookCalls.add(text);
    }
  });

  // Resolve hook dependencies
  hookCalls.forEach((hookName) => {
    const source = importMap.get(hookName);
    if (source) {
      const resolvedPath = resolveModulePath(absPath, source);
      if (resolvedPath) {
        const childTree = buildDependencyTree(resolvedPath, project, maxDepth - 1, new Set(visited));
        result.hooks.push({
          name: hookName,
          source: source,
          dependencies: childTree,
        });
      } else {
        result.hooks.push({
          name: hookName,
          source: source,
          dependencies: null,
        });
      }
    }
  });

  // Extract function calls that might be actions/utils
  callExpressions.forEach((call) => {
    const expression = call.getExpression();
    const text = expression.getText();

    // Skip built-ins, hooks, and component calls
    if (
      !text.startsWith("use") &&
      text[0] === text[0].toLowerCase() &&
      !["console", "JSON", "Math", "Date", "Object", "Array"].some((builtin) => text.startsWith(builtin))
    ) {
      const source = importMap.get(text);
      if (source) {
        const category = source.includes("/api/") || text.includes("fetch") || text.includes("delete") ? "actions" : "utils";

        const resolvedPath = resolveModulePath(absPath, source);
        if (resolvedPath && maxDepth > 1) {
          const childTree = buildDependencyTree(resolvedPath, project, maxDepth - 1, new Set(visited));
          result[category].push({
            name: text,
            source: source,
            dependencies: childTree,
          });
        } else {
          result[category].push({
            name: text,
            source: source,
            dependencies: null,
          });
        }
      }
    }
  });

  // Extract type imports
  imports.forEach((importDecl) => {
    const moduleSpecifier = importDecl.getModuleSpecifierValue();
    if (moduleSpecifier.includes("/types/") || moduleSpecifier.endsWith(".types")) {
      const namedImports = importDecl.getNamedImports().map((ni) => ni.getName());
      namedImports.forEach((name) => {
        result.types.push({
          name: name,
          source: moduleSpecifier,
        });
      });
    }
  });

  return result;
};

const resolveModulePath = (fromFile: string, moduleSpecifier: string): string | null => {
  try {
    // Handle relative imports
    if (moduleSpecifier.startsWith(".")) {
      const dir = path.dirname(fromFile);
      const resolved = path.resolve(dir, moduleSpecifier);

      // Try with extensions
      for (const ext of [".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx"]) {
        const candidate = resolved + ext;
        if (fs.existsSync(candidate)) {
          return candidate;
        }
      }
    }

    // Handle path aliases (@/)
    if (moduleSpecifier.startsWith("@/")) {
      const relativePath = moduleSpecifier.substring(2);
      const webRoot = path.join(projectRoot, "src", "web");
      const resolved = path.join(webRoot, relativePath);

      for (const ext of [".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx"]) {
        const candidate = resolved + ext;
        if (fs.existsSync(candidate)) {
          return candidate;
        }
      }
    }

    return null;
  } catch {
    return null;
  }
};

const analyzeDirectory = (dirPath: string, project: Project, maxFiles: number = 100): any => {
  const files: string[] = [];

  // Only get files from the specified directory, not recursively
  const entries = fs.readdirSync(dirPath);
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry);
    const stat = fs.statSync(fullPath);
    if (stat.isFile() && (entry.endsWith(".ts") || entry.endsWith(".tsx")) && !entry.endsWith(".d.ts")) {
      files.push(fullPath);
    }
  }

  if (files.length > maxFiles) {
    return {
      error: `Too many files (${files.length}). Maximum allowed: ${maxFiles}. Please specify a more specific path.`,
    };
  }

  const result: any = {
    total_files: files.length,
    files: [],
  };

  for (const file of files) {
    try {
      const fileResult = analyzeFile(file, project);
      result.files.push(fileResult);
    } catch (error) {
      // Skip files that fail to analyze
      continue;
    }
  }

  return result;
};

const analyzeConditions = (filePath: string, functionName: string | null, project: Project): any => {
  const sourceFile = project.addSourceFileAtPath(filePath);
  const result: any = {
    file_path: filePath,
    functions: [],
  };

  const builtins = new Set([
    "console", "parseInt", "parseFloat", "isNaN", "isFinite", "decodeURI", "decodeURIComponent",
    "encodeURI", "encodeURIComponent", "eval", "setTimeout", "setInterval", "clearTimeout",
    "clearInterval", "Promise", "Array", "Object", "String", "Number", "Boolean", "Date",
    "Math", "JSON", "RegExp", "Error", "Map", "Set", "WeakMap", "WeakSet", "Symbol",
  ]);

  const isBuiltin = (name: string): boolean => {
    const baseName = name.split(".").pop() || name;
    return builtins.has(baseName);
  };

  const analyzeFunction = (
    func: any,
    name: string,
    isArrowFunction: boolean = false
  ): any => {
    const branches: any[] = [];
    const mockCandidates: any[] = [];
    let complexity = 1;

    const parameters = func.getParameters().map((p: ParameterDeclaration) => {
      const paramName = p.getName();
      const paramType = p.getType().getText();
      const isOptional = p.hasQuestionToken();
      return `${paramName}${isOptional ? "?" : ""}: ${paramType}`;
    });

    const processNode = (node: Node): void => {
      // If statements
      if (node.getKind() === SyntaxKind.IfStatement) {
        const ifStmt = node as any;
        const condition = ifStmt.getExpression().getText();

        branches.push({
          type: "if",
          lineno: ifStmt.getStartLineNumber(),
          end_lineno: ifStmt.getEndLineNumber(),
          condition_code: condition,
        });
        complexity++;

        // Process else if and else
        let current = ifStmt;
        while (current.getElseStatement()) {
          const elseStmt = current.getElseStatement();
          if (elseStmt.getKind() === SyntaxKind.IfStatement) {
            const elseIfCondition = elseStmt.getExpression().getText();
            branches.push({
              type: "else_if",
              lineno: elseStmt.getStartLineNumber(),
              end_lineno: elseStmt.getEndLineNumber(),
              condition_code: elseIfCondition,
            });
            complexity++;
            current = elseStmt;
          } else {
            branches.push({
              type: "else",
              lineno: elseStmt.getStartLineNumber(),
              end_lineno: elseStmt.getEndLineNumber(),
              condition_code: null,
            });
            break;
          }
        }
      }

      // For statements
      if (node.getKind() === SyntaxKind.ForStatement) {
        const forStmt = node as any;
        const initializer = forStmt.getInitializer()?.getText() || "";
        const condition = forStmt.getCondition()?.getText() || "";
        const incrementor = forStmt.getIncrementor()?.getText() || "";
        const conditionCode = `${initializer}; ${condition}; ${incrementor}`;

        branches.push({
          type: "for",
          lineno: forStmt.getStartLineNumber(),
          end_lineno: forStmt.getEndLineNumber(),
          condition_code: conditionCode,
        });
        complexity++;
      }

      // For-of and For-in statements
      if (node.getKind() === SyntaxKind.ForOfStatement || node.getKind() === SyntaxKind.ForInStatement) {
        const forStmt = node as any;
        const initializer = forStmt.getInitializer().getText();
        const expression = forStmt.getExpression().getText();
        const conditionCode = `${initializer} of ${expression}`;

        branches.push({
          type: "for",
          lineno: forStmt.getStartLineNumber(),
          end_lineno: forStmt.getEndLineNumber(),
          condition_code: conditionCode,
        });
        complexity++;
      }

      // While statements
      if (node.getKind() === SyntaxKind.WhileStatement) {
        const whileStmt = node as any;
        const condition = whileStmt.getExpression().getText();

        branches.push({
          type: "while",
          lineno: whileStmt.getStartLineNumber(),
          end_lineno: whileStmt.getEndLineNumber(),
          condition_code: condition,
        });
        complexity++;
      }

      // Do-while statements
      if (node.getKind() === SyntaxKind.DoStatement) {
        const doStmt = node as any;
        const condition = doStmt.getExpression().getText();

        branches.push({
          type: "do_while",
          lineno: doStmt.getStartLineNumber(),
          end_lineno: doStmt.getEndLineNumber(),
          condition_code: condition,
        });
        complexity++;
      }

      // Try-catch statements
      if (node.getKind() === SyntaxKind.TryStatement) {
        const tryStmt = node as any;

        branches.push({
          type: "try",
          lineno: tryStmt.getStartLineNumber(),
          end_lineno: tryStmt.getTryBlock().getEndLineNumber(),
          condition_code: null,
        });

        const catchClause = tryStmt.getCatchClause();
        if (catchClause) {
          const variableDecl = catchClause.getVariableDeclaration();
          const catchVar = variableDecl ? variableDecl.getName() : "error";

          branches.push({
            type: "catch",
            lineno: catchClause.getStartLineNumber(),
            end_lineno: catchClause.getEndLineNumber(),
            condition_code: catchVar,
          });
          complexity++;
        }

        const finallyBlock = tryStmt.getFinallyBlock();
        if (finallyBlock) {
          branches.push({
            type: "finally",
            lineno: finallyBlock.getStartLineNumber(),
            end_lineno: finallyBlock.getEndLineNumber(),
            condition_code: null,
          });
        }
      }

      // Switch statements
      if (node.getKind() === SyntaxKind.SwitchStatement) {
        const switchStmt = node as any;
        const expression = switchStmt.getExpression().getText();

        branches.push({
          type: "switch",
          lineno: switchStmt.getStartLineNumber(),
          end_lineno: switchStmt.getEndLineNumber(),
          condition_code: expression,
        });

        const caseBlock = switchStmt.getCaseBlock();
        if (caseBlock) {
          caseBlock.getClauses().forEach((clause: any) => {
            if (clause.getKind() === SyntaxKind.CaseClause) {
              const caseExpression = clause.getExpression().getText();
              branches.push({
                type: "case",
                lineno: clause.getStartLineNumber(),
                end_lineno: clause.getEndLineNumber(),
                condition_code: caseExpression,
              });
              complexity++;
            } else if (clause.getKind() === SyntaxKind.DefaultClause) {
              branches.push({
                type: "case",
                lineno: clause.getStartLineNumber(),
                end_lineno: clause.getEndLineNumber(),
                condition_code: "default",
              });
            }
          });
        }
      }

      // Ternary/Conditional expressions
      if (node.getKind() === SyntaxKind.ConditionalExpression) {
        const ternary = node as any;
        const condition = ternary.getCondition().getText();

        branches.push({
          type: "ternary",
          lineno: ternary.getStartLineNumber(),
          end_lineno: ternary.getEndLineNumber(),
          condition_code: condition,
        });
        complexity++;
      }

      // Call expressions (for mock candidates)
      if (node.getKind() === SyntaxKind.CallExpression) {
        const callExpr = node as any;
        const expression = callExpr.getExpression();
        let funcName = "";
        let isMethodCall = false;

        if (expression.getKind() === SyntaxKind.PropertyAccessExpression) {
          // e.g., this.repo.save, obj.method
          funcName = expression.getText();
          const expressionText = expression.getExpression().getText();
          isMethodCall = expressionText === "this" || expressionText.startsWith("this.");
        } else if (expression.getKind() === SyntaxKind.Identifier) {
          // e.g., myFunc()
          funcName = expression.getText();
          isMethodCall = false;
        }

        if (funcName && !isBuiltin(funcName)) {
          mockCandidates.push({
            name: funcName,
            lineno: callExpr.getStartLineNumber(),
            end_lineno: callExpr.getEndLineNumber(),
            is_method_call: isMethodCall,
          });
        }
      }

      // Recursively process children (but don't descend into nested functions)
      node.forEachChild((child) => {
        if (
          child.getKind() !== SyntaxKind.FunctionDeclaration &&
          child.getKind() !== SyntaxKind.FunctionExpression &&
          child.getKind() !== SyntaxKind.ArrowFunction &&
          child.getKind() !== SyntaxKind.MethodDeclaration
        ) {
          processNode(child);
        }
      });
    };

    // Process function body
    const body = func.getBody();
    if (body) {
      body.forEachChild((child: Node) => {
        processNode(child);
      });
    }

    return {
      name,
      lineno: func.getStartLineNumber(),
      end_lineno: func.getEndLineNumber(),
      parameters,
      branches,
      mock_candidates: mockCandidates,
      cyclomatic_complexity: complexity,
      is_async: func.isAsync ? func.isAsync() : false,
      is_arrow_function: isArrowFunction,
    };
  };

  // Process top-level functions
  sourceFile.getFunctions().forEach((func) => {
    const name = func.getName();
    if (functionName && name !== functionName) {
      return;
    }
    result.functions.push(analyzeFunction(func, name || "anonymous", false));
  });

  // Process arrow functions in variables
  sourceFile.getVariableDeclarations().forEach((varDecl) => {
    const name = varDecl.getName();
    if (functionName && name !== functionName) {
      return;
    }

    const initializer = varDecl.getInitializer();
    if (initializer && initializer.getKind() === SyntaxKind.ArrowFunction) {
      result.functions.push(analyzeFunction(initializer, name, true));
    }
  });

  // Process class methods
  sourceFile.getClasses().forEach((cls) => {
    cls.getMethods().forEach((method: MethodDeclaration) => {
      const name = method.getName();
      if (functionName && name !== functionName) {
        return;
      }
      result.functions.push(analyzeFunction(method, name, false));
    });
  });

  return result;
};

const main = async (): Promise<void> => {
  const project = new Project({
    tsConfigFilePath: path.join(projectRoot, "src", "web", "tsconfig.json"),
  });

  const arguments_ = process.argv.slice(2);
  const action = arguments_[0];
  const filePath = arguments_[1];
  const symbolName = arguments_[2];
  const searchDirectory = arguments_[3];
  const maxResults = arguments_[4] ? parseInt(arguments_[4], 10) : 100;

  // analyze_file, analyze_directory, dependency_tree, and analyze_conditions don't require symbolName
  if (action !== "analyze_file" && action !== "analyze_directory" && action !== "dependency_tree" && action !== "analyze_conditions") {
    if (!filePath || !symbolName || !action) {
      console.log(JSON.stringify({ error: "Missing required arguments: filePath, symbolName, or action." }, null, 2));
      process.exit(1);
    }
  } else {
    if (!filePath || !action) {
      console.log(JSON.stringify({ error: "Missing required arguments: filePath or action." }, null, 2));
      process.exit(1);
    }
  }

  if (action !== "analyze_directory" && !path.isAbsolute(filePath)) {
    console.log(JSON.stringify({ error: `File path must be absolute: ${filePath}` }, null, 2));
    process.exit(1);
  }

  // For analyze_file, analyze_directory, dependency_tree, and analyze_conditions, add source files first
  if (action === "analyze_file" || action === "analyze_directory" || action === "dependency_tree" || action === "analyze_conditions") {
    // No need to check if file exists for analyze_directory
    if ((action === "analyze_file" || action === "analyze_conditions") && !project.getSourceFile(filePath)) {
      project.addSourceFileAtPath(filePath);
    }
  } else {
    if (!project.getSourceFile(filePath)) {
      project.addSourceFileAtPath(filePath);
    }
  }

  process.stderr.write(`DEBUG: Number of source files in project: ${project.getSourceFiles().length}\n`);

  let result = null;
  try {
    switch (action) {
      case "analyze_file":
        result = analyzeFile(filePath, project);
        break;
      case "analyze_directory":
        result = analyzeDirectory(filePath, project, maxResults);
        break;
      case "dependency_tree":
        {
          const maxDepth = maxResults; // Reuse maxResults parameter for maxDepth
          result = buildDependencyTree(filePath, project, maxDepth);
        }
        break;
      case "analyze_conditions":
        {
          const functionName = symbolName || null;
          result = analyzeConditions(filePath, functionName, project);
        }
        break;
      case "get_type_definitions":
        result = getTypeDefinitions(filePath, symbolName, project);
        break;
      case "get_references":
        result = getReferences(filePath, symbolName, project);
        break;
      case "get_code_snippet":
        result = getCodeSnippet(filePath, symbolName, project);
        break;
      case "get_file_content_snippet":
        result = getFileContentSnippet(filePath);
        break;
      case "get_snippet_and_type_definitions":
        result = getSnippetAndTypeDefinitions(filePath, symbolName, project);
        break;
      case "find_similar_code":
        if (!searchDirectory) {
          console.log(
            JSON.stringify(
              {
                error: "Missing required argument: searchDirectory for find_similar_code.",
              },
              null,
              2
            )
          );
          process.exit(1);
        }
        {
          const baseInfo = getSnippetAndTypeDefinitions(filePath, symbolName, project);
          const matches = findSimilarCode(filePath, symbolName, searchDirectory, maxResults, project);
          result = {
            base_snippet: baseInfo.snippet,
            base_type_definitions: baseInfo.typeDefinitions,
            matches: matches.map((match: any) => ({
              file: match.filePath,
              symbol: match.symbolName,
              similarity: match.similarity,
              snippet: match.snippet,
            })),
          };
        }
        break;
      default:
        process.exit(1);
    }
  } catch (_error) {
    process.stderr.write(`ERROR: ${(_error as Error).message || String(_error)}\n`);
    console.log(JSON.stringify({ error: (_error as Error).message || String(_error) }, null, 2));
    process.exit(1);
  }

  if (typeof result === "string") {
    console.log(result);
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
};

main();
