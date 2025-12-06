/**
 * @fileoverview Disallow snake_case property names in TypeScript/JavaScript
 * @author pipe
 */

const noSnakeCasePropertiesRule = {
  meta: {
    type: 'suggestion',
    docs: {
      description:
        'Disallow snake_case property names (prefer camelCase for consistency)',
      category: 'Stylistic Issues',
      recommended: false
    },
    fixable: 'code',
    schema: [
      {
        type: 'object',
        properties: {
          allowPattern: {
            type: 'string',
            description: 'Regex pattern for allowed snake_case properties'
          },
          ignoreDestructuring: {
            type: 'boolean',
            description: 'Ignore snake_case in destructuring patterns'
          }
        },
        additionalProperties: false
      }
    ],
    messages: {
      snakeCaseProperty:
        "Property '{{name}}' uses snake_case. Use camelCase instead: '{{suggestion}}'",
      snakeCaseKey:
        "Object key '{{name}}' uses snake_case. Use camelCase instead: '{{suggestion}}'"
    }
  },

  create(context) {
    const options = context.options[0] || {}
    const allowPattern = options.allowPattern ? new RegExp(options.allowPattern) : null
    const ignoreDestructuring = options.ignoreDestructuring || false

    function toCamelCase(string_) {
      return string_.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
    }

    function isSnakeCase(name) {
      return /^[a-z]+(_[a-z]+)+$/.test(name)
    }

    function shouldCheck(name) {
      if (!isSnakeCase(name)) return false
      if (allowPattern && allowPattern.test(name)) return false

      return true
    }

    return {
      // Type property signatures: type Foo = { bar_baz: string }
      TSPropertySignature(node) {
        if (node.key.type === 'Identifier') {
          const name = node.key.name
          if (shouldCheck(name)) {
            context.report({
              node: node.key,
              messageId: 'snakeCaseProperty',
              data: {
                name,
                suggestion: toCamelCase(name)
              },
              fix(fixer) {
                return fixer.replaceText(node.key, toCamelCase(name))
              }
            })
          }
        }
      },

      // Member access: obj.foo_bar
      MemberExpression(node) {
        if (node.property.type === 'Identifier' && !node.computed) {
          const name = node.property.name
          if (shouldCheck(name)) {
            context.report({
              node: node.property,
              messageId: 'snakeCaseProperty',
              data: {
                name,
                suggestion: toCamelCase(name)
              },
              fix(fixer) {
                return fixer.replaceText(node.property, toCamelCase(name))
              }
            })
          }
        }
      },

      // Object property definitions: const obj = { foo_bar: 1 }
      Property(node) {
        // Skip if it's a destructuring pattern and ignoreDestructuring is true
        if (ignoreDestructuring && node.parent.type === 'ObjectPattern') {
          return
        }

        // Skip shorthand properties (they'll be caught as Identifier)
        if (node.shorthand) return

        // Skip computed properties
        if (node.computed) return

        if (node.key.type === 'Identifier') {
          const name = node.key.name
          if (shouldCheck(name)) {
            context.report({
              node: node.key,
              messageId: 'snakeCaseKey',
              data: {
                name,
                suggestion: toCamelCase(name)
              },
              fix(fixer) {
                return fixer.replaceText(node.key, toCamelCase(name))
              }
            })
          }
        }
      },

      // Class property definitions: class Foo { bar_baz = 1 }
      PropertyDefinition(node) {
        if (node.key.type === 'Identifier') {
          const name = node.key.name
          if (shouldCheck(name)) {
            context.report({
              node: node.key,
              messageId: 'snakeCaseProperty',
              data: {
                name,
                suggestion: toCamelCase(name)
              },
              fix(fixer) {
                return fixer.replaceText(node.key, toCamelCase(name))
              }
            })
          }
        }
      }
    }
  }
}

export default {
  rules: {
    'no-snake-case-properties': noSnakeCasePropertiesRule
  }
}
