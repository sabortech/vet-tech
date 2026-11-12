query "veterinario/chat" verb=POST {
  api_group = "Support Chat"
  auth = "veterinario"
  input {
    json payload { sensitive = true }
    text bridge_key? { sensitive = true }
  }
  stack {
    conditional {
      if ($input.payload.action == "create") {
        precondition ("veterinario" == "tutor" && $env.SUPPORT_CHAT_BRIDGE_SECRET != null && $env.SUPPORT_CHAT_BRIDGE_SECRET != "" && $input.bridge_key == $env.SUPPORT_CHAT_BRIDGE_SECRET) {
          error_type = "accessdenied"
          error = "Encaminhamento não disponível."
        }
      }
    }
    function.run "Support/operate" {
      input = { profile: "veterinario", actor_id: $auth.id, payload: $input.payload }
    } as $result
  }
  response = $result
  tags = ["vettech", "support-chat"]
  guid = "TFuNvgoc7s75cjhj0Z5rVJ3Mv8E"
}
