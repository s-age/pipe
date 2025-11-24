import fs from 'fs'
import path from 'path'
import { dirname } from 'path'
import { fileURLToPath } from 'url'

import { Project, SyntaxKind } from 'ts-morph'

type ReferenceEntry = {
  filePath: string
  line?: number
  lineNumber?: number
  column: number
  snippet: string
}

type TypeDefinition = {
  type?: string
  properties?: any[]
  methods?: any[]
  parameters?: any[]
  returnType?: string
  propsType?: string
  props?: any[]
  variableType?: string
  definition?: string
}

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const projectRoot = path.join(__dirname, '..', '..', '..')

const getTypeDefinitions = (
  filePath: string,
  symbolName: string,
  project: Project
): TypeDefinition | null => {
  const sourceFile = project.addSourceFileAtPath(filePath)
  const definitions: TypeDefinition = {}

  // Find class declarations
  const classDeclaration = sourceFile.getClass(symbolName)
  if (classDeclaration) {
    definitions.type = 'class'
    definitions.properties = classDeclaration.getProperties().map((p) => ({
      name: p.getName(),
      type: p.getType().getText(),
      isStatic: p.isStatic(),
      isReadonly: p.isReadonly()
    }))
    definitions.methods = classDeclaration.getMethods().map((m) => ({
      name: m.getName(),
      parameters: m.getParameters().map((p) => ({
        name: p.getName(),
        type: p.getType().getText()
      })),
      returnType: m.getReturnType().getText(),
      isStatic: m.isStatic()
    }))

    return definitions
  }

  // Find function declarations
  const functionDeclaration = sourceFile.getFunction(symbolName)
  if (functionDeclaration) {
    definitions.type = 'function'
    definitions.parameters = functionDeclaration.getParameters().map((p) => ({
      name: p.getName(),
      type: p.getType().getText()
    }))
    definitions.returnType = functionDeclaration.getReturnType().getText()

    return definitions
  }

  // Find variable declarations (const, let, var)
  const variableDeclaration = sourceFile.getVariableDeclaration(symbolName)
  if (variableDeclaration) {
    const initializer = variableDeclaration.getInitializer()

    // Check if it's an arrow function component
    if (initializer && initializer.getKind() === SyntaxKind.ArrowFunction) {
      const arrowFunction = initializer
      // @ts-expect-error ts-morph API
      const parameters = arrowFunction.getParameters()
      // @ts-expect-error ts-morph API
      const returnType = arrowFunction.getReturnType().getText()

      if (parameters.length > 0) {
        const firstParameter = parameters[0]
        const firstParameterType = firstParameter.getTypeNode()

        if (
          firstParameterType &&
          firstParameterType.getKind() === SyntaxKind.TypeReference
        ) {
          const propertiesTypeName = firstParameterType.getText()
          const propertiesInterface = sourceFile.getInterface(propertiesTypeName)
          const propertiesTypeAlias = sourceFile.getTypeAlias(propertiesTypeName)

          if (propertiesInterface) {
            definitions.type = 'React.ArrowFunctionComponent'
            definitions.propsType = propertiesTypeName
            definitions.returnType = returnType
            definitions.props = propertiesInterface.getProperties().map((p) => ({
              name: p.getName(),
              type: p.getType().getText(),
              isOptional: p.hasQuestionToken()
            }))

            return definitions
          } else if (propertiesTypeAlias) {
            definitions.type = 'React.ArrowFunctionComponent'
            definitions.propsType = propertiesTypeName
            definitions.returnType = returnType
            const aliasedType = propertiesTypeAlias.getType()
            const properties = aliasedType.getProperties()
            if (properties) {
              definitions.props = properties.map((p) => ({
                name: p.getName(),
                type: p.getTypeAtLocation(propertiesTypeAlias).getText(),
                // @ts-expect-error ts-morph internal
                isOptional: p.compilerObject ? p.compilerObject.flags & 16777216 : false
              }))
            } else {
              definitions.props = []
            }

            return definitions
          }
        }
      }
      // If no specific Props type is found but it's an arrow function
      definitions.type = 'React.ArrowFunctionComponent'
      definitions.parameters = parameters.map((p: any) => ({
        name: p.getName(),
        type: p.getType().getText()
      }))
      definitions.returnType = returnType

      return definitions
    }

    definitions.type = 'variable'
    definitions.variableType = variableDeclaration.getType().getText()

    return definitions
  }

  // Find interfaces
  const interfaceDeclaration = sourceFile.getInterface(symbolName)
  if (interfaceDeclaration) {
    definitions.type = 'interface'
    definitions.properties = interfaceDeclaration.getProperties().map((p) => ({
      name: p.getName(),
      type: p.getType().getText()
    }))

    return definitions
  }

  // Find type aliases
  const typeAliasDeclaration = sourceFile.getTypeAlias(symbolName)
  if (typeAliasDeclaration) {
    definitions.type = 'typeAlias'
    definitions.definition = typeAliasDeclaration.getTypeNode()!.getText()

    return definitions
  }

  return null
}

const getReferences = (
  filePath: string,
  symbolName: string,
  project: Project
): ReferenceEntry[] => {
  const references: ReferenceEntry[] = []

  const symbol = project
    .getSourceFiles()
    .flatMap((sf) => sf.getDescendantsOfKind(SyntaxKind.Identifier))
    .find((id) => id.getText() === symbolName)

  if (symbol) {
    const symbolReferences = symbol.findReferencesAsNodes()
    symbolReferences.forEach((reference) => {
      const start = reference.getStart()
      const sourceFile = reference.getSourceFile()
      const lineAndColumn = sourceFile.getLineAndColumnAtPos(start)
      references.push({
        filePath: sourceFile.getFilePath(),
        lineNumber: lineAndColumn.line,
        column: lineAndColumn.column,
        snippet: sourceFile.getFullText().split('\n')[lineAndColumn.line - 1].trim()
      })
    })
  }

  return references
}

const getCodeSnippet = (
  filePath: string,
  symbolName: string,
  project: Project
): string | null => {
  const sourceFile = project.addSourceFileAtPath(filePath)

  // Try to find a class, function, variable, interface, or type alias
  const declaration =
    sourceFile.getClass(symbolName) ||
    sourceFile.getFunction(symbolName) ||
    sourceFile.getInterface(symbolName) ||
    sourceFile.getTypeAlias(symbolName)

  if (declaration) {
    return declaration.getText()
  }

  // Try to find a variable declaration, including default exports
  const variableDeclarations = sourceFile.getVariableDeclarations()
  for (const variableDecl of variableDeclarations) {
    if (variableDecl.getName() === symbolName) {
      const initializer = variableDecl.getInitializer()
      if (initializer && initializer.getKind() === SyntaxKind.ArrowFunction) {
        // For arrow function components, return the entire variable statement
        return variableDecl.getParent().getText()
      }

      return variableDecl.getText()
    }
  }

  // If not found by name, check for default export if the symbol name matches the file name
  const fileNameWithoutExtension = path.parse(filePath).name
  if (symbolName === fileNameWithoutExtension) {
    const defaultExportSymbol = sourceFile.getDefaultExportSymbol()
    if (defaultExportSymbol) {
      const declarations = defaultExportSymbol.getDeclarations()
      for (const decl of declarations) {
        if (
          decl.getKind() === SyntaxKind.VariableDeclaration ||
          decl.getKind() === SyntaxKind.VariableStatement
        ) {
          return decl.getText()
        }
      }
    }
  }

  return null
}

const getFileContentSnippet = (filePath: string): string | null => {
  try {
    return fs.readFileSync(filePath, 'utf8')
  } catch {
    return null
  }
}

const getSnippetAndTypeDefinitions = (
  filePath: string,
  symbolName: string,
  project: Project
): { snippet: string | null; typeDefinitions: TypeDefinition | null } => {
  const snippet = getCodeSnippet(filePath, symbolName, project)
  const typeDefinitions = getTypeDefinitions(filePath, symbolName, project)

  return { snippet, typeDefinitions }
}

const calculateSimilarity = (string1: string, string2: string): number => {
  const m = string1.length
  const n = string2.length
  const dp = Array(m + 1)
    .fill(0)
    .map(() => Array(n + 1).fill(0))

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (string1[i - 1] === string2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1])
      }
    }
  }
  const lcs = dp[m][n]

  return (2 * lcs) / (m + n)
}

const getExportedSymbols = (filePath: string, project: Project): string[] => {
  const sourceFile = project.addSourceFileAtPath(filePath)
  const exportedDeclarations = sourceFile.getExportedDeclarations()
  const symbols: string[] = []

  for (const [name] of exportedDeclarations) {
    symbols.push(name)
  }

  return symbols
}

const findSimilarCode = (
  baseFilePath: string,
  symbolName: string,
  searchDirectory: string,
  maxResults: number = 3,
  project: Project
): ReferenceEntry[] => {
  const baseInfo = getSnippetAndTypeDefinitions(baseFilePath, symbolName, project)
  if (!baseInfo.snippet) {
    console.error(
      `DEBUG: No base snippet found for symbol '${symbolName}' in ${baseFilePath}`
    )

    return []
  }

  const baseSnippet = baseInfo.snippet

  const tsFiles: string[] = []
  const walkSync = (currentDirectory: string): void => {
    const files = fs.readdirSync(currentDirectory)
    for (const file of files) {
      const fullPath = path.join(currentDirectory, file)
      const stat = fs.statSync(fullPath)
      if (stat.isDirectory()) {
        if (file !== 'node_modules') {
          walkSync(fullPath)
        }
      } else if (
        (file.endsWith('.ts') || file.endsWith('.tsx')) &&
        !file.endsWith('.css.ts')
      ) {
        process.stderr.write(`DEBUG: Found TS/TSX file: ${fullPath}\n`)
        tsFiles.push(fullPath)
      } else {
        process.stderr.write(
          `DEBUG: Skipping non-TS/TSX or .css.ts file: ${fullPath}\n`
        )
      }
    }
  }
  walkSync(searchDirectory)
  process.stderr.write(`DEBUG: Total TS/TSX files found: ${tsFiles.length}\n`)

  const similarCodes: any[] = []

  for (const filePath of tsFiles) {
    if (path.resolve(filePath) === path.resolve(baseFilePath)) {
      process.stderr.write(`DEBUG: Skipping base file: ${filePath}\n`)
      continue
    }

    const exportedSymbols = getExportedSymbols(filePath, project)
    process.stderr.write(
      `DEBUG: Exported symbols in ${filePath}: ${exportedSymbols.join(', ')}\n`
    )

    for (const targetSymbol of exportedSymbols) {
      const otherSnippet = getCodeSnippet(filePath, targetSymbol, project)
      if (otherSnippet) {
        const similarity = calculateSimilarity(baseSnippet, otherSnippet)
        process.stderr.write(
          `DEBUG: Comparing ${symbolName} (base) with ${targetSymbol} (${filePath}). Similarity: ${similarity}\n`
        )
        if (similarity > 0.5) {
          // 類似度の閾値
          process.stderr.write(
            `DEBUG: Found similar code (similarity > 0.5): ${targetSymbol} in ${filePath}\n`
          )
          similarCodes.push({
            file_path: filePath,
            symbol_name: targetSymbol,
            similarity: similarity,
            snippet: otherSnippet
          })
        } else {
          process.stderr.write(
            `DEBUG: Similarity below threshold (0.5): ${targetSymbol} in ${filePath}\n`
          )
        }
      } else {
        process.stderr.write(
          `DEBUG: No snippet found for symbol '${targetSymbol}' in ${filePath}\n`
        )
      }
    }
  }

  similarCodes.sort((a, b) => b.similarity - a.similarity)

  return similarCodes.slice(0, maxResults)
}

const main = async (): Promise<void> => {
  const project = new Project({
    tsConfigFilePath: path.join(projectRoot, 'src', 'web', 'tsconfig.json')
  })

  const arguments_ = process.argv.slice(2)
  const filePath = arguments_[0]
  const symbolName = arguments_[1]
  const action = arguments_[2]
  const searchDirectory = arguments_[3]
  const maxResults = arguments_[4] ? parseInt(arguments_[4], 10) : 3

  if (!filePath || !symbolName || !action) {
    console.log(
      JSON.stringify(
        { error: 'Missing required arguments: filePath, symbolName, or action.' },
        null,
        2
      )
    )
    process.exit(1)
  }

  if (!path.isAbsolute(filePath)) {
    console.log(
      JSON.stringify({ error: `File path must be absolute: ${filePath}` }, null, 2)
    )
    process.exit(1)
  }

  // project.addSourceFilesFromTsConfig(path.join(projectRoot, 'src', 'web', 'tsconfig.json'), {
  //     tsConfigFilePath: path.join(projectRoot, 'src', 'web', 'tsconfig.json'),
  //     basePath: path.join(projectRoot, 'src', 'web')
  // });

  if (!project.getSourceFile(filePath)) {
    project.addSourceFileAtPath(filePath)
  }

  process.stderr.write(
    `DEBUG: Number of source files in project: ${project.getSourceFiles().length}\n`
  )

  let result = null
  try {
    switch (action) {
      case 'get_type_definitions':
        result = getTypeDefinitions(filePath, symbolName, project)
        break
      case 'get_references':
        result = getReferences(filePath, symbolName, project)
        break
      case 'get_code_snippet':
        result = getCodeSnippet(filePath, symbolName, project)
        break
      case 'get_file_content_snippet':
        result = getFileContentSnippet(filePath)
        break
      case 'get_snippet_and_type_definitions':
        result = getSnippetAndTypeDefinitions(filePath, symbolName, project)
        break
      case 'find_similar_code':
        if (!searchDirectory) {
          console.log(
            JSON.stringify(
              {
                error:
                  'Missing required argument: searchDirectory for find_similar_code.'
              },
              null,
              2
            )
          )
          process.exit(1)
        }
        result = findSimilarCode(
          filePath,
          symbolName,
          searchDirectory,
          maxResults,
          project
        )
        break
      default:
        process.exit(1)
    }
  } catch (_error) {
    process.stderr.write(`ERROR: ${(_error as Error).message || String(_error)}\n`)
    console.log(
      JSON.stringify({ error: (_error as Error).message || String(_error) }, null, 2)
    )
    process.exit(1)
  }

  if (typeof result === 'string') {
    console.log(result)
  } else {
    console.log(JSON.stringify(result, null, 2))
  }
}

main()
