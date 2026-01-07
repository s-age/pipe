/**
 * ESLint rule to enforce that destructuring parameter order matches the type definition order.
 */

const getPropertyName = (property) => {
  if (property.type === 'TSPropertySignature' && property.key?.type === 'Identifier') {
    return property.key.name
  }
  if (property.type === 'Property' && property.key?.type === 'Identifier') {
    return property.key.name
  }

  return null
}

const getDestructuredPropertyName = (property) => {
  if (property.type === 'Property' && property.key?.type === 'Identifier') {
    return property.key.name
  }

  return null
}

const findTypeDefinition = (context, typeName) => {
  const sourceCode = context.sourceCode || context.getSourceCode()
  const ast = sourceCode.ast

  let typeDefinition = null
  const visited = new WeakSet()

  const traverse = (node) => {
    if (!node || typeof node !== 'object' || visited.has(node)) {
      return
    }

    visited.add(node)

    if (
      node.type === 'TSTypeAliasDeclaration' &&
      node.id &&
      node.id.name === typeName &&
      node.typeAnnotation &&
      node.typeAnnotation.type === 'TSTypeLiteral'
    ) {
      typeDefinition = node.typeAnnotation

      return
    }

    // Traverse child nodes
    for (const key in node) {
      if (Object.prototype.hasOwnProperty.call(node, key)) {
        const value = node[key]
        if (value && typeof value === 'object') {
          if (Array.isArray(value)) {
            for (const child of value) {
              traverse(child)
            }
          } else if (key !== 'parent' && key !== 'loc' && key !== 'range') {
            traverse(value)
          }
        }
      }
    }
  }

  traverse(ast)

  return typeDefinition
}

const getTypeDefinitionFromAnnotation = (node) => {
  // node is ObjectPattern
  let typeAnnotation = null

  // Check if type annotation is on ObjectPattern itself
  if (node.typeAnnotation && node.typeAnnotation.typeAnnotation) {
    typeAnnotation = node.typeAnnotation.typeAnnotation
  }
  // Check if type annotation is on parent VariableDeclarator
  else if (
    node.parent &&
    node.parent.type === 'VariableDeclarator' &&
    node.parent.typeAnnotation &&
    node.parent.typeAnnotation.typeAnnotation
  ) {
    typeAnnotation = node.parent.typeAnnotation.typeAnnotation
  }

  if (!typeAnnotation) {
    return null
  }

  // Case 1: Named type reference (type Props = { ... })
  if (
    typeAnnotation.type === 'TSTypeReference' &&
    typeAnnotation.typeName.type === 'Identifier'
  ) {
    return { type: 'named', typeName: typeAnnotation.typeName.name }
  }

  // Case 2: Inline type literal ({ ... }: { ... })
  if (typeAnnotation.type === 'TSTypeLiteral') {
    return { type: 'inline', typeDefinition: typeAnnotation }
  }

  return null
}

const findFunctionReturnType = (context, functionName) => {
  const sourceCode = context.sourceCode || context.getSourceCode()
  const ast = sourceCode.ast

  let returnTypeDefinition = null
  const visited = new WeakSet()

  const traverse = (node) => {
    if (!node || typeof node !== 'object' || visited.has(node)) {
      return
    }

    visited.add(node)

    // Look for: export const useFoo = (): ReturnType => { ... }
    if (
      (node.type === 'FunctionDeclaration' || node.type === 'VariableDeclarator') &&
      node.id &&
      node.id.name === functionName
    ) {
      // For VariableDeclarator, check the init (arrow function)
      const functionNode =
        node.type === 'VariableDeclarator' && node.init ? node.init : node

      if (functionNode.returnType && functionNode.returnType.typeAnnotation) {
        const returnType = functionNode.returnType.typeAnnotation

        // Case 1: Named type reference
        if (
          returnType.type === 'TSTypeReference' &&
          returnType.typeName &&
          returnType.typeName.type === 'Identifier'
        ) {
          const typeName = returnType.typeName.name
          returnTypeDefinition = findTypeDefinition(context, typeName)

          return
        }

        // Case 2: Inline type literal
        if (returnType.type === 'TSTypeLiteral') {
          returnTypeDefinition = returnType

          return
        }
      }
    }

    // Traverse child nodes
    for (const key in node) {
      if (Object.prototype.hasOwnProperty.call(node, key)) {
        const value = node[key]
        if (value && typeof value === 'object') {
          if (Array.isArray(value)) {
            for (const child of value) {
              traverse(child)
            }
          } else if (key !== 'parent' && key !== 'loc' && key !== 'range') {
            traverse(value)
          }
        }
      }
    }
  }

  traverse(ast)

  return returnTypeDefinition
}

const getHookNameFromCallExpression = (node) => {
  // node is ObjectPattern, check if parent is VariableDeclarator with CallExpression init
  if (
    !node.parent ||
    node.parent.type !== 'VariableDeclarator' ||
    !node.parent.init ||
    node.parent.init.type !== 'CallExpression'
  ) {
    return null
  }

  const callExpression = node.parent.init
  if (
    callExpression.callee &&
    callExpression.callee.type === 'Identifier' &&
    callExpression.callee.name.startsWith('use')
  ) {
    return callExpression.callee.name
  }

  return null
}

const pluginMatchPropertiesOrder = {
  meta: {
    type: 'layout',
    docs: {
      description:
        'Enforce that destructuring parameter order matches the type definition order',
      category: 'Stylistic Issues',
      recommended: false
    },
    fixable: 'code',
    schema: []
  },

  create(context) {
    const sourceCode = context.sourceCode || context.getSourceCode()

    return {
      ObjectPattern(node) {
        const { properties } = node
        if (!properties || properties.length === 0) {
          return
        }

        let typeDefinition = null

        // Try to get type definition from annotation first
        const typeInfo = getTypeDefinitionFromAnnotation(node)

        if (typeInfo) {
          // Handle named type reference
          if (typeInfo.type === 'named') {
            typeDefinition = findTypeDefinition(context, typeInfo.typeName)
          }
          // Handle inline type literal
          else if (typeInfo.type === 'inline') {
            typeDefinition = typeInfo.typeDefinition
          }
        } else {
          // No type annotation - check if this is a hook call destructuring
          const hookName = getHookNameFromCallExpression(node)
          if (hookName) {
            typeDefinition = findFunctionReturnType(context, hookName)
          }
        }

        // If we couldn't find a type definition, skip
        if (!typeDefinition || !typeDefinition.members) {
          return
        }

        // Extract property names from type definition
        const typePropertyNames = typeDefinition.members
          .filter((member) => member.type === 'TSPropertySignature')
          .map((member) => getPropertyName(member))
          .filter(Boolean)

        // Extract property names from destructuring
        const destructuredProperties = properties.filter(
          (property) => property.type === 'Property'
        )
        const destructuredPropertyNames = destructuredProperties.map((property) =>
          getDestructuredPropertyName(property)
        )

        // Check if all destructured properties exist in type definition
        const allExist = destructuredPropertyNames.every((name) =>
          typePropertyNames.includes(name)
        )
        if (!allExist) {
          return
        }

        // Sort destructured properties based on type definition order
        const sorted = [...destructuredProperties].sort((a, b) => {
          const nameA = getDestructuredPropertyName(a)
          const nameB = getDestructuredPropertyName(b)
          const indexA = typePropertyNames.indexOf(nameA)
          const indexB = typePropertyNames.indexOf(nameB)

          return indexA - indexB
        })

        // Check if order is incorrect
        const isIncorrect = destructuredProperties.some(
          (property, index) => property !== sorted[index]
        )

        if (isIncorrect) {
          context.report({
            node,
            message:
              'Destructured properties should match the order defined in the type definition',
            fix(fixer) {
              const firstProperty = destructuredProperties[0]
              const lastProperty = destructuredProperties.at(-1)
              const start = firstProperty.range[0]
              const end = lastProperty.range[1]

              // Generate sorted text preserving newlines
              const hasNewlines = sourceCode.getText(node).split('\n').length > 1

              let newText = ''
              if (hasNewlines) {
                const sortedTexts = sorted.map((property) => {
                  const text = sourceCode.getText(property)

                  return text
                })

                // Determine indentation from first property
                const indent = ' '.repeat(firstProperty.loc.start.column)
                newText = sortedTexts.join(',\n' + indent)
              } else {
                const sortedTexts = sorted.map((property) => {
                  const text = sourceCode.getText(property)

                  return text
                })
                newText = sortedTexts.join(', ')
              }

              return fixer.replaceTextRange([start, end], newText)
            }
          })
        }
      }
    }
  }
}

// eslint-disable-next-line import/no-default-export
export default {
  rules: {
    'match-props-order': pluginMatchPropertiesOrder
  }
}
