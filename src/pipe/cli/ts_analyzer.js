import fs from "fs";
import path from "path";

import { Project, SyntaxKind } from "ts-morph";

import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = path.join(__dirname, "..", "..", "..");

function getTypeDefinitions(filePath, symbolName, project) {
  const sourceFile = project.addSourceFileAtPath(filePath);
  const definitions = {};

  // Find class declarations
  const classDeclaration = sourceFile.getClass(symbolName);
  if (classDeclaration) {
    definitions.type = "class";
    definitions.properties = classDeclaration.getProperties().map((p) => ({
      name: p.getName(),
      type: p.getType().getText(),
      isStatic: p.isStatic(),
      isReadonly: p.isReadonly(),
    }));
    definitions.methods = classDeclaration.getMethods().map((m) => ({
      name: m.getName(),
      parameters: m.getParameters().map((p) => ({
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
    definitions.parameters = functionDeclaration.getParameters().map((p) => ({
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
      const arrowFunction = initializer;
      const parameters = arrowFunction.getParameters();
      const returnType = arrowFunction.getReturnType().getText();

      if (parameters.length > 0) {
        const firstParam = parameters[0];
        const firstParamType = firstParam.getTypeNode();

        if (firstParamType && firstParamType.getKind() === SyntaxKind.TypeReference) {
          const propsTypeName = firstParamType.getText();
          const propsInterface = sourceFile.getInterface(propsTypeName);
          const propsTypeAlias = sourceFile.getTypeAlias(propsTypeName);

          if (propsInterface) {
            definitions.type = "React.ArrowFunctionComponent";
            definitions.propsType = propsTypeName;
            definitions.returnType = returnType;
            definitions.props = propsInterface.getProperties().map((p) => ({
              name: p.getName(),
              type: p.getType().getText(),
              isOptional: p.hasQuestionToken(),
            }));

            return definitions;
          } else if (propsTypeAlias) {
            definitions.type = "React.ArrowFunctionComponent";
            definitions.propsType = propsTypeName;
            definitions.returnType = returnType;
            const aliasedType = propsTypeAlias.getType();
            definitions.props = aliasedType.getProperties().map((p) => ({
              name: p.getName(),
              type: p.getTypeAtLocation(propsTypeAlias).getText(),
              isOptional: p.compilerObject.flags & 16777216,
            }));

            return definitions;
          }
        }
      }
      // If no specific Props type is found but it's an arrow function
      definitions.type = "React.ArrowFunctionComponent";
      definitions.parameters = parameters.map((p) => ({
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
    definitions.properties = interfaceDeclaration.getProperties().map((p) => ({
      name: p.getName(),
      type: p.getType().getText(),
    }));

    return definitions;
  }

  // Find type aliases
  const typeAliasDeclaration = sourceFile.getTypeAlias(symbolName);
  if (typeAliasDeclaration) {
    definitions.type = "typeAlias";
    definitions.definition = typeAliasDeclaration.getTypeNode().getText();

    return definitions;
  }

  return null;
}

function getReferences(filePath, symbolName, project) {
  const references = [];

  const symbol = project
    .getSourceFiles()
    .flatMap((sf) => sf.getDescendantsOfKind(SyntaxKind.Identifier))
    .find((id) => id.getText() === symbolName);

  if (symbol) {
    const symbolReferences = symbol.findReferencesAsNodes();
    symbolReferences.forEach((ref) => {
      references.push({
        filePath: ref.getSourceFile().getFilePath(),
        lineNumber: ref.getStartLineNumber(),
        lineContent: ref
          .getSourceFile()
          .getFullText()
          .split("\n")
          [ref.getStartLineNumber() - 1].trim(),
      });
    });
  }

  return references;
}

function getCodeSnippet(filePath, symbolName, project) {
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

  // Try to find a variable declaration, including default exports
  const variableDeclarations = sourceFile.getVariableDeclarations();
  for (const varDecl of variableDeclarations) {
    if (varDecl.getName() === symbolName) {
      const initializer = varDecl.getInitializer();
      if (initializer && initializer.getKind() === SyntaxKind.ArrowFunction) {
        // For arrow function components, return the entire variable statement
        return varDecl.getParent().getText();
      }

      return varDecl.getText();
    }
  }

  // If not found by name, check for default export if the symbol name matches the file name
  const fileNameWithoutExtension = path.parse(filePath).name;
  if (symbolName === fileNameWithoutExtension) {
    const defaultExportSymbol = sourceFile.getDefaultExportSymbol();
    if (defaultExportSymbol) {
      const declarations = defaultExportSymbol.getDeclarations();
      for (const decl of declarations) {
        if (
          decl.getKind() === SyntaxKind.VariableDeclaration ||
          decl.getKind() === SyntaxKind.VariableStatement
        ) {
          return decl.getText();
        }
      }
    }
  }

  return null;
}

function getFileContentSnippet(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return null;
  }
}

function getSnippetAndTypeDefinitions(filePath, symbolName, project) {
  const snippet = getCodeSnippet(filePath, symbolName, project);
  const typeDefinitions = getTypeDefinitions(filePath, symbolName, project);

  return { snippet, typeDefinitions };
}

function calculateSimilarity(str1, str2) {
  const m = str1.length;
  const n = str2.length;
  const dp = Array(m + 1)
    .fill(0)
    .map(() => Array(n + 1).fill(0));

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (str1[i - 1] === str2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }
  const lcs = dp[m][n];

  return (2 * lcs) / (m + n);
}

function findSimilarCode(
  baseFilePath,
  symbolName,
  searchDirectory,
  maxResults = 3,
  project,
) {
  const baseInfo = getSnippetAndTypeDefinitions(baseFilePath, symbolName, project);
  if (!baseInfo.snippet) {
    console.error(
      `DEBUG: No base snippet found for symbol '${symbolName}' in ${baseFilePath}`,
    );

    return {
      error: `No code snippet found for symbol '${symbolName}' in ${baseFilePath}`,
    };
  }

  const baseSnippet = baseInfo.snippet;
  const baseTypeDefinitions = baseInfo.typeDefinitions;

  const tsFiles = [];
  function walkSync(currentDir) {
    const files = fs.readdirSync(currentDir);
    for (const file of files) {
      const fullPath = path.join(currentDir, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        if (file !== "node_modules") {
          walkSync(fullPath);
        }
      } else if (
        (file.endsWith(".ts") || file.endsWith(".tsx")) &&
        !file.endsWith(".css.ts")
      ) {
        process.stderr.write(`DEBUG: Found TS/TSX file: ${fullPath}\n`);
        tsFiles.push(fullPath);
      } else {
        process.stderr.write(
          `DEBUG: Skipping non-TS/TSX or .css.ts file: ${fullPath}\n`,
        );
      }
    }
  }
  walkSync(searchDirectory);
  process.stderr.write(`DEBUG: Total TS/TSX files found: ${tsFiles.length}\n`);

  const similarCodes = [];

  for (const filePath of tsFiles) {
    if (path.resolve(filePath) === path.resolve(baseFilePath)) {
      process.stderr.write(`DEBUG: Skipping base file: ${filePath}\n`);
      continue;
    }

    let targetSymbol = path.parse(filePath).name;
    if (targetSymbol === "index") {
      targetSymbol = path.basename(path.dirname(filePath));
      process.stderr.write(
        `DEBUG: Inferred symbol for index.tsx: ${targetSymbol} from ${filePath}\n`,
      );
    } else {
      process.stderr.write(
        `DEBUG: Using file name as symbol: ${targetSymbol} for ${filePath}\n`,
      );
    }

    const otherSnippet = getCodeSnippet(filePath, targetSymbol, project);
    if (otherSnippet) {
      const similarity = calculateSimilarity(baseSnippet, otherSnippet);
      process.stderr.write(
        `DEBUG: Comparing ${symbolName} (base) with ${targetSymbol} (${filePath}). Similarity: ${similarity}\n`,
      );
      if (similarity > 0.5) {
        // 類似度の閾値
        process.stderr.write(
          `DEBUG: Found similar code (similarity > 0.5): ${targetSymbol} in ${filePath}\n`,
        );
        similarCodes.push({
          file_path: filePath,
          symbol_name: targetSymbol,
          similarity: similarity,
          snippet: otherSnippet,
        });
      } else {
        process.stderr.write(
          `DEBUG: Similarity below threshold (0.5): ${targetSymbol} in ${filePath}\n`,
        );
      }
    } else {
      process.stderr.write(
        `DEBUG: No snippet found for symbol '${targetSymbol}' in ${filePath}\n`,
      );
    }
  }

  similarCodes.sort((a, b) => b.similarity - a.similarity);

  return {
    base_symbol_type_definitions: baseTypeDefinitions,
    similar_codes: similarCodes.slice(0, maxResults),
  };
}

async function main() {
  const project = new Project({
    tsConfigFilePath: path.join(projectRoot, "src", "web", "tsconfig.json"),
  });

  const args = process.argv.slice(2);
  const filePath = args[0];
  const symbolName = args[1];
  const action = args[2];
  const searchDirectory = args[3];
  const maxResults = args[4] ? parseInt(args[4], 10) : 3;

  if (!filePath || !symbolName || !action) {
    console.log(
      JSON.stringify(
        { error: "Missing required arguments: filePath, symbolName, or action." },
        null,
        2,
      ),
    );
    process.exit(1);
  }

  if (!path.isAbsolute(filePath)) {
    console.log(
      JSON.stringify({ error: `File path must be absolute: ${filePath}` }, null, 2),
    );
    process.exit(1);
  }

  // project.addSourceFilesFromTsConfig(path.join(projectRoot, 'src', 'web', 'tsconfig.json'), {
  //     tsConfigFilePath: path.join(projectRoot, 'src', 'web', 'tsconfig.json'),
  //     basePath: path.join(projectRoot, 'src', 'web')
  // });

  if (!project.getSourceFile(filePath)) {
    project.addSourceFileAtPath(filePath);
  }

  process.stderr.write(
    `DEBUG: Number of source files in project: ${project.getSourceFiles().length}\n`,
  );

  let result = null;
  try {
    switch (action) {
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
                error:
                  "Missing required argument: searchDirectory for find_similar_code.",
              },
              null,
              2,
            ),
          );
          process.exit(1);
        }
        result = findSimilarCode(
          filePath,
          symbolName,
          searchDirectory,
          maxResults,
          project,
        );
        break;
      default:
        process.exit(1);
    }
  } catch (_error) {
    process.stderr.write(`ERROR: ${_error.message || String(_error)}\n`);
    console.log(JSON.stringify({ error: _error.message || String(_error) }, null, 2));
    process.exit(1);
  }

  if (typeof result === "string") {
    console.log(result);
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
}

main();
