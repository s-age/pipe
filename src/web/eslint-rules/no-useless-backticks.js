// Local ESLint rule: no-useless-backticks
// Detects template literals without variable interpolation and suggests converting to regular strings.

const plugin = {
  rules: {
    'no-useless-backticks': {
      meta: {
        type: 'suggestion',
        docs: {
          description: 'Disallow template literals without variable interpolation',
          recommended: true
        },
        fixable: 'code',
        schema: [],
        messages: {
          noUselessBackticks:
            'Template literal has no interpolations, use a regular string instead.'
        }
      },
      create: (context) => ({
        TemplateLiteral: (node) => {
          // Check if there are any interpolations (expressions)
          if (node.expressions.length === 0) {
            // Check if the template has any escaped backticks or newlines that would make it different
            const sourceCode = context.getSourceCode()
            const text = sourceCode.getText(node)

            // Remove the backticks and check if it's a valid string literal
            const innerText = text.slice(1, -1)

            // If it contains backticks or newlines, it might need to be a template literal
            if (innerText.includes('`') || innerText.includes('\n')) {
              return
            }

            // Determine quote type: prefer single quotes unless the string contains single quotes
            const quote = innerText.includes("'") ? '"' : "'"
            const replacement =
              quote + innerText.replace(new RegExp(quote, 'g'), '\\' + quote) + quote

            context.report({
              node,
              messageId: 'noUselessBackticks',
              fix: (fixer) => fixer.replaceText(node, replacement)
            })
          }
        }
      })
    }
  }
}

export default plugin
