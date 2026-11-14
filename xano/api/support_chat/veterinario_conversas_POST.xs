query "veterinario/conversas" verb=POST {
  api_group = "Support Chat"
  auth = "veterinario"
  input { json payload { sensitive = true } }
  stack {
    function.run "Direct/operate" {
      input = {profile: "veterinario", actor_id: $auth.id, payload: $input.payload}
    } as $result
  }
  response = $result
  tags = ["vettech", "direct-messaging"]
  guid = "yWVUZH2KsOnFd6ZJ_g__4QMtc7Q"
}
