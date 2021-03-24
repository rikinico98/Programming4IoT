// POST

// FUNZIONE PER L'INSERIMENTO DEL DEVICE
function sendDevicesPOSTrequest() {
  event.preventDefault();
  // tutti i passi seguenti servono per costruire il json nel modo corretto
  
  //leggo tutti gli input dalla form html com l'id/name che hanno
  roomID = $("#roomID").val();
  deviceID = $("#deviceID").val();
  deviceName = $("#deviceName").val();
  measureType = $("#measureType").val();
  field = $("#field").val();

  service1 = $("#service1").val();
  serviceip1 = $("#serviceIP").val();
  service1_topic1 = $("#topic1").val();
  service1_topic2 = $("#topic2").val();
  service1_topic3 = $("#topic3").val();

 // se i topics non sono vuoti allora si crea la lista definitiva dei topics
  topics_service1 = [service1_topic1, service1_topic2,service1_topic3];
  topics1_array = [];
  var k = 0;
  for (i=0; i<3; i++){
    if (topics_service1[i] != ""){
      topics1_array[k] = topics_service1[i];
      k = k+1;
    }
  }
  
  service2 = $("#service2").val();
  serviceip2 = $("#serviceIP2").val();
  service2_topic1 = $("#topic11").val();
  service2_topic2 = $("#topic22").val();
  service2_topic3 = $("#topic33").val();

  // se i topics non sono vuoti allora si crea la lista definitiva dei topics
  topics_service2 = [service2_topic1, service2_topic2,service2_topic3];
  topics2_array = [];
  var k = 0;
  for (i=0; i<3; i++){
    if (topics_service2[i] != ""){
      topics2_array[k] = topics_service2[i];
      k = k+1;
    }
  }

  // anche i services bisogna controllare, se il secondo è NULL allora
  // vuol dire che ce n'è solo 1 e bisogna eliminare i campi nulli della form

  services_array = [service1, service2];
  services = [];
  services_details = [];

  if (services_array[1] == 'none'){
    services = services_array[0];
    services_details = {
      serviceType: service1,
      serviceIP: serviceip1,
      topic: topics1_array
    }
  }else{
    services = services_array;
    services_details = [{
      serviceType: service1,
      serviceIP: serviceip1,
      topic: topics1_array 
    },
    {
      serviceType: service2,
      serviceIP: serviceip2,
      topic: topics2_array
    }]
  }
  
  // il body è quello che verrà poi inviato nel catalog, mentre il command andrà a definire l'ulr
  body = {
    roomID : roomID,
    deviceID: deviceID,
    deviceName: deviceName,
    measureType: measureType,
    availableServices : services,
    servicesDetails: services_details,
    field: field,
    }; 

  $.ajax({
    type: "POST",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: "insert_device", body:body}),
    dataType: "json",
  });
}
// FUNZIONE PER L'INSERIMENTO DELLA STANZA
function sendRoomsPOSTrequest() {
  event.preventDefault();
  roomID = $("#room_ID").val();
  product_type = $("#product_type").val();
  temp_min = parseInt($("#temp_min").val());
  temp_max = parseInt($("#temp_max").val());
  hum_min = parseInt($("#hum_min").val());
  hum_max = parseInt($("#hum_max").val());
  smoke_min = parseInt($("#smoke_min").val());
  smoke_max = parseInt($("#smoke_max").val());

  body = {
    roomID : roomID,
    devicesList: [],
    ranges: {"Temperature": [temp_min,temp_max], "Humidity": [hum_min, hum_max], "Smoke": [smoke_min, smoke_max]},
    product_type: product_type,
    ThingSpeak:{"channelID": "", "api_key_read": "", "api_key_write": ""}
    };

    $.ajax({
      type: "POST",
      url: "/",
      contentType: "application/json",
      data: JSON.stringify({command: "insert_room", body:body}),
      dataType: "json",
    });

}
// FUNZIONE PER L'AGGIORNAMENTO DELL'UTENTE
function sendUsersPOSTrequest(){
  event.preventDefault();
  roomID = String($("#roomIDs").val());
  userID = $("#userID").val(); 
  roomIDs = [];

  if (roomID.search("-") != -1){
    roomIDs = roomID.split("-");    
  }else{roomIDs = [roomID]}

  body = {
    roomIDs : roomIDs,
    userID: userID,
    chatID: ""
  };

    $.ajax({
      type: "POST",
      url: "/",
      contentType: "application/json",
      data: JSON.stringify({command: "insert_user", body:body}),
      dataType: "json",
    });

}

// // ROOM UPDATE (PUT)

/* api_key_update {“api_key_read”: ZVBAO2QDON8B19X0} catalog/ID_stanza/TS_get */
function sendRoomApiKeyReadPUTrequest(){
  roomID = $("#roomID3").val();
  api_key_read = $("#api_key_r").val();  
  command = 'update_api_key_read';
  body = {
    roomID : roomID,
    api_key_read : api_key_read
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });

}
// api_key_write {“api_key_write”: S6ULMDXZPCVFBR0H}  catalog/ID_stanza/TS_post
function sendRoomApiKeyWritePUTrequest(){
  roomID = $("#roomID4").val();
  api_key_write = $("#api_key_w").val();  
  command = 'update_api_key_write';
  body = {
    roomID : roomID,
    api_key_write : api_key_write
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}
/*channel id {“channelID”: 134252} catalog/ID_stanza/TS_channel*/
function sendRoomChannelPUTrequest(){

  roomID = $("#roomID_2").val();
  channelID= $("#chann_id").val();  
  command = "update_channel_id";
  body = {
    roomID : roomID,
    channelID : channelID
  };

  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });  
}
// update product type {"product_type": "00"} catalog/ID_stanza/change_product_type
function sendRoomProductPUTrequest(){
  roomID1 = $("#roomID_1").val();
  product_type = $("#prod_type").val();  
  command = 'update_product_type';
  body = {
    roomID : roomID1,
    product_type : product_type
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}
// update temperature ranges
function sendRoomTemperaturePUTrequest() {
  roomID1 = $("#roomID5").val();
  temp_min = parseInt($("#temp_min_1").val());  
  temp_max = parseInt($("#temp_max_1").val()); 
  command = 'change_ranges';
  body = {
    roomID : roomID1,
    ranges:{Temperature : [temp_min, temp_max]}
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}
function sendRoomHumidityPUTrequest() {
  roomID1 = $("#roomID6").val();
  hum_min = parseInt($("#hum_min_1").val());  
  hum_max = parseInt($("#hum_max_1").val()); 
  command = 'change_ranges';
  body = {
    roomID : roomID1,
    ranges:{Humidity : [hum_min, hum_max]}
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}
function sendRoomSmokePUTrequest() {
  roomID1 = $("#roomID7").val();
  smoke_min = parseInt($("#smoke_min_1").val());  
  smoke_max = parseInt($("#smoke_max_1").val()); 
  command = 'change_ranges';
  body = {
    roomID : roomID1,
    ranges:{Smoke : [smoke_min, smoke_max]}
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}

// devices updates

// change name {"deviceName":"Pippo"} catalog/ID_stanza/ID_device/update_name
function sendDeviceNamePUTrequest(){
  room = $("#room").val();
  device_id = $("#device_id").val();  
  device_name = $("#device_name").val(); 
  command = 'update_name';
  body = {
    roomID : room,
    deviceID: device_id,
    deviceName : device_name
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}
// change measure Type  catalog/ID_stanza/ID_device/change_meas_type ->{"measureType":"Celsius"}
function sendDeviceMeasurePUTrequest(){
  room = $("#roomD").val();
  device_id = $("#device_idD").val();  
  meas_type = $("#meas_typeD").val(); 
  command = 'change_meas_type';
  body = {
    roomID : room,
    deviceID: device_id,
    measureType : meas_type
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}

// change services details catalog/ID_stanza/ID_device/change_service_details ->{"servicesDetails": [
//      {   "serviceType": "MQTT",
//          "serviceIP": "mqtt.eclipse.org",
//          "topic": [
//             "MySmartThingy/1/temp",
//              "MySmartThingy/1/hum" ]},
//        {  "serviceType": "REST",
//          "serviceIP": "dht11.org:8080",
//          "topic": [] }
//          ] }
function sendDeviceServicePUTrequest(){
    //leggo tutti gli input dalla form html com l'id/name che hanno
    roomID = $("#roomid").val();
    deviceID = $("#device_Id").val();
    
    service1 = $("#service_1").val();
    serviceip1 = $("#service__IP").val();
    service1_topic1 = $("#topic111").val();
    service1_topic2 = $("#topic222").val();
    service1_topic3 = $("#topic333").val();
  
   // se i topics non sono vuoti allora si crea la lista definitiva dei topics
    topics_service1 = [service1_topic1, service1_topic2,service1_topic3];
    topics1_array = [];
    var k = 0;
    for (i=0; i<3; i++){
      if (topics_service1[i] != ""){
        topics1_array[k] = topics_service1[i];
        k = k+1;
      }
    }
    
    service2 = $("#service_2").val();
    serviceip2 = $("#service__IP2").val();
    service2_topic1 = $("#topic_11").val();
    service2_topic2 = $("#topic_22").val();
    service2_topic3 = $("#topic_33").val();
  
    // se i topics non sono vuoti allora si crea la lista definitiva dei topics
    topics_service2 = [service2_topic1, service2_topic2,service2_topic3];
    topics2_array = [];
    var k = 0;
    for (i=0; i<3; i++){
      if (topics_service2[i] != ""){
        topics2_array[k] = topics_service2[i];
        k = k+1;
      }
    }
  
    // anche i services bisogna controllare, se il secondo è NULL allora
    // vuol dire che ce n'è solo 1 e bisogna eliminare i campi nulli della form
  
    services_array = [service1, service2];
    services = [];
    services_details = [];
  
    if (services_array[1] == 'none'){
      services = services_array[0];
      services_details = {
        serviceType: service1,
        serviceIP: serviceip1,
        topic: topics1_array
      }
    }else{
      services = services_array;
      services_details = [{
        serviceType: service1,
        serviceIP: serviceip1,
        topic: topics1_array 
      },
      {
        serviceType: service2,
        serviceIP: serviceip2,
        topic: topics2_array
      }]
    }
    
    // il body è quello che verrà poi inviato nel catalog, mentre il command andrà a definire l'ulr
    body = {
      roomID : roomID,
      deviceID: deviceID,
      availableServices : services,
      servicesDetails: services_details
      }; 
  
    $.ajax({
      type: "PUT",
      url: "/",
      contentType: "application/json",
      data: JSON.stringify({command: "add_service_details", body:body}),
      dataType: "json",
    });

}

// change topics catalog/ID_stanza/ID_device/change_topic {"topic": ["MySmartThingy/1/temp","MySmartThingy/1/hum"]}
function sendDeviceTopicPUTrequest(){
    room = $("#room__D").val();
    device_id = $("#device__idD").val();  
    topic = $("#topic_D").val(); 
    command = 'change_topic';
    topics = [];
    
    if (topic.search("-") != -1){
      topics = topic.split("-");    
    }else{topics = [topic]}

    body = {
      roomID : room,
      deviceID: device_id,
      topic : topics
    };
    $.ajax({
      type: "PUT",
      url: "/",
      contentType: "application/json",
      data: JSON.stringify({command: command, body:body}),
      dataType: "json",
    }); 
}
// change field catalog/ID_stanza/ID_Device/change_field ->  {"field": 'field1'}
function sendDeviceFieldPUTrequest(){
  room = $("#roomID10").val();
  device_id = $("#device_id123").val();  
  field = $("#field_123").val(); 
  command = 'change_field';

  body = {
    roomID : room,
    deviceID: device_id,
    field: field
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });

}

//PUT USERS
//add a room /catalog/User_ID/add_asigned_rooms 
function sendUserRoomsAddPUTrequest(){
  userID = $("#user_id").val();
  roomID = $("#rooms").val();
  command = 'add_assigned_rooms';

  rooms = [];    
    if (roomID.search("-") != -1){
      rooms = roomID.split("-");    
    }else{rooms = [roomID]}

  body = {
    roomIDs : rooms,
    userID: userID
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}
//remove a room /catalog/User_ID/delete_asigned_rooms 
function sendUserRoomsDeletePUTrequest(){
  userID = $("#user_id").val();
  roomID = $("#rooms").val();
  command = 'delete_assigned_rooms';

  rooms = [];    
    if (roomID.search("-") != -1){
      rooms = roomID.split("-");    
    }else{rooms = [roomID]}

  body = {
    roomIDs : rooms,
    userID: userID
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}

//change role {"userID": "nuovo_userID"}
function sendUserRolePUTrequest(){
  olduserID = $("#old_user_id").val();
  userID = $("#new_user_id").val();
  command = 'change_role';

  body = {
    olduserID : olduserID,
    userID: userID
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}

//DELETE FUNCTIONS
function sendDeviceDeleteRequest(){
  roomID = $("#id_room").val();
  deviceID = $("#id_device").val();
  command = 'delete_device';

  body = {
    roomID : roomID,
    deviceID: deviceID
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}
function sendUserDeleteRequest(){
  userID = $("#id_user").val();
  command = 'delete_user';

  body = {
    userID : userID
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
  
}
function sendRoomDeleteRequest(){
  roomID = $("#id1_room").val();
  command = 'delete_room';

  body = {
    roomID : roomID
  };
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}

function sendRoomPUTrequest(){
}

function sendDevicePUTrequest(){
}
