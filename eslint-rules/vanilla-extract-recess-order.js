// Local ESLint plugin: vanilla-extract/recess-order
// Detects `style({...})` and `styleVariants({...})` object literals and
// reorders top-level CSS properties according to a configured recess-like order.
// This file exports a plugin object consumable by the flat ESLint config.

// eslint-disable-next-line import/no-default-export
export default {
  rules: {
    'recess-order': {
      meta: {
        type: 'suggestion',
        docs: {
          description:
            'Enforce a consistent property order for vanilla-extract style objects',
          recommended: false
        },
        fixable: 'code',
        schema: [
          {
            type: 'object',
            properties: {
              order: { type: 'array', items: { type: 'string' } }
            },
            additionalProperties: false
          }
        ],
        messages: {
          reorder: 'Style properties should follow the configured recess order.'
        }
      },
      // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
      create(context) {
        const sourceCode = context.getSourceCode()

        // Default ordering (simplified recess-like order). Lower index = earlier.
        const defaultOrder = [
          // Positioning/Layout
          'display',
          'position',
          'top',
          'right',
          'bottom',
          'left',
          'float',
          'clear',
          'flex',
          'grid',
          'order',
          'width',
          'minWidth',
          'maxWidth',
          'height',
          'minHeight',
          'maxHeight',
          'boxSizing',
          'overflow',
          'overflowX',
          'overflowY',
          // Box model
          'margin',
          'marginTop',
          'marginRight',
          'marginBottom',
          'marginLeft',
          'padding',
          'paddingTop',
          'paddingRight',
          'paddingBottom',
          'paddingLeft',
          'border',
          'borderWidth',
          'borderStyle',
          'borderColor',
          'borderRadius',
          // Typography
          'font',
          'fontFamily',
          'fontSize',
          'fontWeight',
          'lineHeight',
          'letterSpacing',
          'textAlign',
          'color',
          // Visuals
          'background',
          'backgroundColor',
          'backgroundImage',
          'backgroundPosition',
          'backgroundSize',
          'boxShadow',
          // Interaction
          'cursor',
          'userSelect',
          'pointerEvents',
          'opacity',
          'transition',
          'transform'
        ]

        // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
        function getKeyName(property) {
          if (property.key.type === 'Identifier') return property.key.name
          if (property.key.type === 'Literal') return String(property.key.value)

          return sourceCode.getText(property.key)
        }

        // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
        function compareProperties(a, b, order) {
          const an = getKeyName(a)
          const bn = getKeyName(b)
          const ai = order.indexOf(an)
          const bi = order.indexOf(bn)
          const A = ai === -1 ? Number.MAX_SAFE_INTEGER : ai
          const B = bi === -1 ? Number.MAX_SAFE_INTEGER : bi
          if (A !== B) return A - B

          // fallback to original order to be stable
          return 0
        }

        return {
          // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
          CallExpression(node) {
            // match style({...}) or styleVariants({...}) calls
            const callee = node.callee
            if (callee.type !== 'Identifier') return
            if (!(callee.name === 'style' || callee.name === 'styleVariants')) return

            const arguments_ = node.arguments
            if (!arguments_ || arguments_.length === 0) return

            const first = arguments_[0]
            if (first.type !== 'ObjectExpression') return

            const properties = first.properties.filter((p) => p.type === 'Property')
            if (properties.length <= 1) return

            const options = context.options && context.options[0]
            const order = (options && options.order) || defaultOrder

            const sorted = [...properties].sort((a, b) =>
              compareProperties(a, b, order)
            )

            // Check if order differs
            let differs = false
            for (let i = 0; i < properties.length; i++) {
              if (properties[i] !== sorted[i]) {
                differs = true
                break
              }
            }
            if (!differs) return

            context.report({
              node: first,
              messageId: 'reorder',
              // eslint-disable-next-line no-restricted-syntax
              fix(fixer) {
                // Reconstruct the object literal contents using source text of properties
                const propertyTexts = sorted.map((p) => sourceCode.getText(p))
                // preserve original spacing by joining with ',\n'
                // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
                const indent = (() => {
                  const start = first.range[0]
                  const loc = sourceCode.getLocFromIndex(start)
                  const line = loc.line
                  const lineText = sourceCode.lines[line - 1] || ''
                  const m = lineText.match(/^\s*/)

                  return m ? m[0] + '  ' : '  '
                })()

                const joined = propertyTexts.map((t) => indent + t).join(',\n')

                // Replace the object contents between the braces
                const openBrace = first.range[0]
                const closeBrace = first.range[1]
                const replacement = '{\n' + joined + '\n}'

                return fixer.replaceTextRange([openBrace, closeBrace], replacement)
              }
            })
          }
        }
      }
    }
  }
}
