

class FilledForm {
  @@dynamic
}

function FillForm(user_message: string) -> FilledForm {
  client "CustomGenericProvider"
  prompt #"
    You are given a conversation with a customer:
      {{ user_message }}
    Extract all relevant information from the conversation and fill in the form.
    Ensure that you follow the structure of the form template provided below.
    Provide the filled form in the following format:
    {{ ctx.output_format }}
  "#
}

// Test the function with a sample resume. Open the VSCode playground to run this.
test dummy_custommer_feedback {
  functions [FillForm]
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
