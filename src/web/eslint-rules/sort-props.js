/**
 * ESLint rule to enforce consistent property ordering in Props types and destructuring.
 * Order: required variables, optional variables, required functions, optional functions.
 */

const isFunction = (node) =>
  // Function types in TypeScript
  node.type === 'TSFunctionType' ||
  (node.type === 'TSTypeReference' &&
    node.typeName &&
    node.typeName.name &&
    /^(React\.)?((Mouse|Keyboard|Touch|Focus|Form|Change|Click|Key|UI|Pointer|Wheel|Animation|Transition|Clipboard|Composition|Drag)Event|EventHandler|ChangeEventHandler|MouseEventHandler|KeyboardEventHandler|FormEventHandler|FocusEventHandler|TouchEventHandler|PointerEventHandler|WheelEventHandler|AnimationEventHandler|TransitionEventHandler|ClipboardEventHandler|CompositionEventHandler|DragEventHandler|UIEventHandler)$/.test(
      node.typeName.name
    )) ||
  (node.type === 'TSParenthesizedType' && isFunction(node.typeAnnotation))

const getPropertyCategory = (property) => {
  // Get type annotation
  let typeAnnotation = null
  if (property.type === 'TSPropertySignature') {
    typeAnnotation = property.typeAnnotation?.typeAnnotation
  } else if (property.type === 'Property') {
    typeAnnotation = property.value?.typeAnnotation?.typeAnnotation
  }

  const isOptional = property.optional || false
  const isFunctionType = typeAnnotation && isFunction(typeAnnotation)

  // Return category: 0 = required var, 1 = optional var, 2 = required fn, 3 = optional fn
  if (isFunctionType) {
    return isOptional ? 3 : 2
  }

  return isOptional ? 1 : 0
}

const getPropertyName = (property) => {
  if (property.key?.type === 'Identifier') {
    return property.key.name
  }

  return ''
}

const compareProperties = (a, b) => {
  const categoryA = getPropertyCategory(a)
  const categoryB = getPropertyCategory(b)

  if (categoryA !== categoryB) {
    return categoryA - categoryB
  }

  // Same category: alphabetically
  const nameA = getPropertyName(a)
  const nameB = getPropertyName(b)

  return nameA.localeCompare(nameB)
}

const sortProperties = (properties) => [...properties].sort(compareProperties)

const pluginSortProperties = {
  meta: {
    type: 'layout',
    docs: {
      description:
        'Enforce consistent property ordering: required vars, optional vars, required functions, optional functions',
      category: 'Stylistic Issues',
      recommended: false
    },
    fixable: 'code',
    schema: []
  },

  create(context) {
    const sourceCode = context.sourceCode || context.getSourceCode()

    return {
      // Type aliases: type Props = { ... }
      TSTypeLiteral(node) {
        const { members } = node
        if (!members || members.length === 0) {
          return
        }

        // Skip inline type literals (handled by match-props-order)
        // Only process type aliases: type Props = { ... }
        const parent = node.parent
        if (!parent || parent.type !== 'TSTypeAliasDeclaration') {
          return
        }

        // Filter only property signatures
        const properties = members.filter(
          (member) => member.type === 'TSPropertySignature'
        )

        if (properties.length === 0) {
          return
        }

        const sorted = sortProperties(properties)
        const original = properties

        // Check if order is incorrect
        const isIncorrect = original.some(
          (property, index) => property !== sorted[index]
        )

        if (isIncorrect) {
          context.report({
            node,
            message:
              'Properties should be ordered: required variables, optional variables, required functions, optional functions',
            fix(fixer) {
              const firstProperty = properties[0]
              const lastProperty = properties.at(-1)
              const start = firstProperty.range[0]
              const end = lastProperty.range[1]

              // Generate sorted text
              const sortedTexts = sorted.map((property) => {
                const text = sourceCode.getText(property)

                return text
              })

              const indent = ' '.repeat(firstProperty.loc.start.column)
              const newText = sortedTexts.join('\n' + indent)

              return fixer.replaceTextRange([start, end], newText)
            }
          })
        }
      },

      // Object pattern in function parameters: ({ a, b }: Props) => { ... }
      ObjectPattern(node) {
        const { properties } = node
        if (!properties || properties.length === 0) {
          return
        }

        // Skip if has type annotation - let match-props-order handle it
        if (node.typeAnnotation) {
          return
        }

        // Skip if this is a hook call destructuring - let match-props-order handle it
        if (
          node.parent &&
          node.parent.type === 'VariableDeclarator' &&
          node.parent.init &&
          node.parent.init.type === 'CallExpression' &&
          node.parent.init.callee &&
          node.parent.init.callee.type === 'Identifier' &&
          node.parent.init.callee.name.startsWith('use')
        ) {
          return
        }

        // Filter only properties (not rest elements)
        const properties_ = properties.filter(
          (property) => property.type === 'Property'
        )

        if (properties_.length === 0) {
          return
        }

        const sorted = sortProperties(properties_)
        const original = properties_

        // Check if order is incorrect
        const isIncorrect = original.some(
          (property, index) => property !== sorted[index]
        )

        if (isIncorrect) {
          context.report({
            node,
            message:
              'Destructured properties should be ordered: required variables, optional variables, required functions, optional functions',
            fix(fixer) {
              const firstProperty = properties_[0]
              const lastProperty = properties_.at(-1)
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
    'sort-props': pluginSortProperties
  }
}
