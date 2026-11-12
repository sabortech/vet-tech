query "tutor/chat" verb=POST {
  api_group = "Support Chat"
  auth = "tutor"
  input {
    json payload { sensitive = true }
    text bridge_key? { sensitive = true }
  }
  stack {
    conditional {
      if ($input.payload.action == "create") {
        precondition ("tutor" == "tutor" && $env.SUPPORT_CHAT_BRIDGE_SECRET != null && $env.SUPPORT_CHAT_BRIDGE_SECRET != "" && $input.bridge_key == $env.SUPPORT_CHAT_BRIDGE_SECRET) {
          error_type = "accessdenied"
          error = "Encaminhamento não disponível."
        }
      }
    }
    function.run "Support/operate" {
      input = { profile: "tutor", actor_id: $auth.id, payload: $input.payload }
    } as $result
  }
  response = $result
  tags = ["vettech", "support-chat"]
  guid = "63t9OG-IjWox1-CBDkzPfYBp_Iw"
}
