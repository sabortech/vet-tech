query "tutor/pets/{pet_id}/historico" verb=GET {
  api_group = "Clinical"
  auth = "tutor"
  input {
    int pet_id
  }
  stack {
    function.run "Clinical/assert_owner" {
      input = {
        pet_id: $input.pet_id, tutor_id: $auth.id
      }
    } as $owned
    function.run "Clinical/history" {
      input = {
        pet_id: $owned.id
      }
    } as $reply
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "Z2ox3NSrRInNwrYZyLLMtvYXQK8"
}
