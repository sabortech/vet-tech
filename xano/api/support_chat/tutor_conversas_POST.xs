query "tutor/conversas" verb=POST {
  api_group = "Support Chat"
  auth = "tutor"
  input { json payload { sensitive = true } }
  stack {
    function.run "Direct/operate" {
      input = {profile: "tutor", actor_id: $auth.id, payload: $input.payload}
    } as $result
  }
  response = $result
  tags = ["vettech", "direct-messaging"]
  guid = "LmMV_jyrwBggjuQMXALbY-eqcXk"
}
