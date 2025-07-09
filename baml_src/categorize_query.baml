
class Feedback {
  rationale string @description("the rationale for the choice")
  category int @description("category choosen")
}

class ClassificationValue {
  title string @description("the title of the category")
  description string @description("the description of the category")
}

function CategorizeFeedback(user_message: string, categories: ClassificationValue[]) -> Feedback {
  client "CustomGenericProvider"
  prompt #"
    Categorize the following user message:
      {{ user_message }}
    into one of the following categories:
    {% for c in categories %}
      Category {{loop.index}}: {{c.title}} // {{c.description}}
    {% if loop.last %}
    The categories are numbered from 1 to {{ loop.index }}.
    {% endif %}
    {% endfor %}
    Provide the category number and a brief rationale for your choice.
    {{ ctx.output_format }}
  "#
}

// Test the function with a sample resume. Open the VSCode playground to run this.
test dummy_custommer_feedback {
  functions [CategorizeFeedback]
  args {
    user_message #"
      I am calling because I have a problem with my internet connection
    "#
    categories [
        {
            title "Technical support",
            description "The customer is calling for technical support"
        },
        {
            title "Billing",
            description "The customer is calling for billing issues"
        },
        {
            title "Refund",
            description "The customer is calling for a refund"
        }
    ]
  }
}
