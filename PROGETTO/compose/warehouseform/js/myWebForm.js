/* tutte le funzioni qui presenti vengono richiamate dalla form al click dei vari button e servono per inviare delle richieste
POST e PUT al Register che a sua volta legge il body di queste richieste che contiene un "command" e in base a questo
effettua le giuste richieste POST, PUT, DELETE al catalog */

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
  field2 = $("#field2").val();
  // primo service della form
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
  // secondo service della form
  service2 = $("#service2_http").val();
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

  // anche i services bisogna controllare, se il secondo è "none" allora
  // vuol dire che ce n'è solo 1 e bisogna eliminare i campi nulli della form

  services_array = [service1, service2];
  services = [];
  services_details = [];

  if (services_array[1] == 'none'){
    services = services_array[0];
    services_details = [{
      serviceType: service1,
      serviceIP: serviceip1,
      topic: topics1_array
    }]
  };
  // tutte le combinazioni dei service che possono essere selezionati e la costruzione dei campi del body
  if (services_array[1] == 'REST' && services_array[0] == 'MQTT'){
    services = services_array;
    services_details = [{
      serviceType: service1,
      serviceIP: serviceip1,
      topic: topics1_array 
    },
    {
      serviceType: service2,
      serviceIP: serviceip2
    }]
  };

  if (services_array[1] == 'MQTT' && services_array[0] == 'REST'){
    services = services_array;
    services_details = [{
      serviceType: service1,
      serviceIP: serviceip1
    }, {
      serviceType: service2,
      serviceIP: serviceip2,
      topic: topics2_array 
    }]
  };

  if (services_array[1] == 'MQTT' && services_array[0] == 'MQTT') {
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
  };
  // necessario nel caso in cui come nel DHT11 è necessario avere più fields
  // o come nel caso del blackout in cui non se ne hanno
  fields = [];
  if (field2 == 'none' && field != 'none') {
    fields = [field];
  } else if (field2 != 'none' && field == 'none') {
    fields = [field2];
  } else if (field2 != 'none' && field != 'none') {
    fields = [field, field2];
  } else {
    fields = [];
  }
  // il body è quello che verrà poi inviato nel catalog, mentre il command andrà a definire l'ulr
  body = {
    roomID : roomID,
    deviceID: deviceID,
    deviceName: deviceName,
    measureType: measureType,
    availableServices : services,
    servicesDetails: services_details,
    field: fields
    }; 
    // richiesta post da effettuare al register
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
  // si pendono i campi dalla form
  roomID = $("#room_ID").val();
  product_type = $("#product_type").val();
  temp_min = parseInt($("#temp_min").val());
  temp_max = parseInt($("#temp_max").val());
  hum_min = parseInt($("#hum_min").val());
  hum_max = parseInt($("#hum_max").val());
  smoke_min = parseInt($("#smoke_min").val());
  // costruzione del body da inviare
  body = {
    roomID : roomID,
    devicesList: [],
    ranges: {"Temperature": [temp_min,temp_max], "Humidity": [hum_min, hum_max], "Smoke": [smoke_min]},
    product_type: product_type,
    ThingSpeak:{"channelID": "", "api_key_read": "", "api_key_write": ""}
    };
    // richiesta POST al Register
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
  // se sono più stanze le separo con il trattino come indicato sulla form
  if (roomID.search("-") != -1){
    roomIDs = roomID.split("-");    
  }else{roomIDs = [roomID]}
  // costruzione del body
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
// ************************ROOM UPDATE (PUT)************************************
/* api_key_update {“api_key_read”: ZVBAO2QDON8B19X0} catalog/ID_stanza/TS_get -> MODIFICA API KEY READ */ 
function sendRoomApiKeyReadPUTrequest(){
  // leggo i campi dalla form
  roomID = $("#roomID3").val();
  api_key_read = $("#api_key_r").val();  
  command = 'update_api_key_read';
  // costruzione del body
  body = {
    roomID : roomID,
    api_key_read : api_key_read
  };
  // richiesta PUT alla form
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });

}
// api_key_write {“api_key_write”: S6ULMDXZPCVFBR0H}  catalog/ID_stanza/TS_post -> MODIFICA API KEY WRITE
function sendRoomApiKeyWritePUTrequest(){
  // leggo i campi dalla form
  roomID = $("#roomID4").val();
  api_key_write = $("#api_key_w").val();  
  command = 'update_api_key_write';
  // costruisco il body
  body = {
    roomID : roomID,
    api_key_write : api_key_write
  };
  // put request
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}
/*channel id {“channelID”: 134252} catalog/ID_stanza/TS_channel* -> MODIFICA CHANNEL ID */
function sendRoomChannelPUTrequest(){
  // leggo i campi dalla form
  roomID = $("#roomID_2").val();
  channelID= $("#chann_id").val();  
  command = "update_channel_id";
  // costruisco il body
  body = {
    roomID : roomID,
    channelID : channelID
  };
  // richiesta PUT al register
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });  
}
// update product type {"product_type": "00"} catalog/ID_stanza/change_product_type -> MODIFICA DEL PRODUCT TYPE
function sendRoomProductPUTrequest(){
  // leggo i campi dalla form
  roomID1 = $("#roomID_1").val();
  product_type = $("#prod_type").val();  
  command = 'update_product_type';
  // costruisco il body
  body = {
    roomID : roomID1,
    product_type : product_type
  };
  // richiesta PUT 
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}
// update temperature ranges {"ranges": {"Temperature":[min, max]}} -> MODIFICA DEI RANGES DI TEMPERATURA
function sendRoomTemperaturePUTrequest() {
  // leggo i campi dalla form
  roomID1 = $("#roomID5").val();
  temp_min = parseInt($("#temp_min_1").val());  
  temp_max = parseInt($("#temp_max_1").val()); 
  command = 'change_ranges';
  // costruisco il body
  body = {
    roomID : roomID1,
    ranges:{Temperature : [temp_min, temp_max]}
  };
  // invio la richiesta
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}
// update Humidity ranges {"ranges": {"Humidity":[min, max]}} -> MODIFICA DEI RANGES DI umidità
function sendRoomHumidityPUTrequest() {
  // leggo i campi della form
  roomID1 = $("#roomID6").val();
  hum_min = parseInt($("#hum_min_1").val());  
  hum_max = parseInt($("#hum_max_1").val()); 
  command = 'change_ranges';
  // costruisco il body
  body = {
    roomID : roomID1,
    ranges:{Humidity : [hum_min, hum_max]}
  };
  // richiesta PUT
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}
// update Smoke ranges ranges {"ranges": {"Smoke":[min, max]}} -> MODIFICA DEI RANGES DI smoke
function sendRoomSmokePUTrequest() {
  // leggo i campi dalla form
  roomID1 = $("#roomID7").val();
  smoke_min = parseInt($("#smoke_min_1").val());
  command = 'change_ranges';
  // costruisco il body
  body = {
    roomID : roomID1,
    ranges:{Smoke : [smoke_min]}
  };
  // richiesta PUT
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  }); 
}

// ***************************devices updates*******************************************
// change name {"deviceName":"Pippo"} catalog/ID_stanza/ID_device/update_name
function sendDeviceNamePUTrequest(){
  // leggo i campi dalla form
  room = $("#room").val();
  device_id = $("#device_id").val();  
  device_name = $("#device_name").val(); 
  command = 'update_name';
  // costruisco il body
  body = {
    roomID : room,
    deviceID: device_id,
    deviceName : device_name
  };
  // faccio una richiesta PUT
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
  // leggo i campi dalla form
  room = $("#roomD").val();
  device_id = $("#device_idD").val();  
  meas_type = $("#meas_typeD").val(); 
  command = 'change_meas_type';
  // costruisco il body
  body = {
    roomID : room,
    deviceID: device_id,
    measureType : meas_type
  };
  // richiesta PUT
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
    // primo service della form
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
    // secondo service della form
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
    // anche i services bisogna controllare, se il secondo è none allora
    // vuol dire che ce n'è solo 1 e bisogna eliminare i campi nulli della form  
    services_array = [service1, service2];
    services = [];
    services_details = [];  
    if (services_array[1] == 'none'){
      services = services_array[0];
      services_details = [{
        serviceType: service1,
        serviceIP: serviceip1,
        topic: topics1_array
      }]
    };
    // tutte le possibile scelte dalla form per costruire bene i campi del body
    if (services_array[1] == 'REST' && services_array[0] == 'MQTT'){
      services = services_array;
      services_details = [{
        serviceType: service1,
        serviceIP: serviceip1,
        topic: topics1_array 
      },
      {
        serviceType: service2,
        serviceIP: serviceip2
      }]
    };

    if (services_array[1] == 'MQTT' && services_array[0] == 'REST'){
      services = services_array;
      services_details = [{
        serviceType: service1,
        serviceIP: serviceip1
      }, {
        serviceType: service2,
        serviceIP: serviceip2,
        topic: topics2_array 
      }]
    };
  
    if (services_array[1] == 'MQTT' && services_array[0] == 'MQTT') {
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
    };
    
    // costruisco il body che è quello che verrà poi inviato nel catalog, mentre il command andrà a definire l'ulr
    body = {
      roomID : roomID,
      deviceID: deviceID,
      availableServices : services,
      servicesDetails: services_details
      }; 
    // richiesta PUT al Register
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
    // leggo i campi dalla form
    room = $("#room__D").val();
    device_id = $("#device__idD").val();  
    topic = $("#topic_D").val(); 
    command = 'change_topic';
    topics = [];
    // se sono più di 1 creo una lista separando i campi dai '-'
    if (topic.search("-") != -1){
      topics = topic.split("-");    
    }else{topics = [topic]}
    // creo il body
    body = {
      roomID : room,
      deviceID: device_id,
      topic : topics
    };
    // richiesta PUT al Register
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
  // leggo i campi della form
  room = $("#roomID10").val();
  device_id = $("#device_id123").val();  
  field = $("#field_123").val(); 
  field2 = $("#field_2").val(); 
  command = 'change_field';
  // necessario nel caso in cui come nel DHT11 è necessario avere più fields
  // o come nel caso del blackout in cui non se ne hanno
  fields = [];
  if (field2 == 'none' && field != 'none') {
    fields = [field];
  } else if (field2 != 'none' && field == 'none') {
    fields = [field2];
  } else if (field2 != 'none' && field != 'none') {
    fields = [field, field2];
  } else {
    fields = [];
  }
  // costruisco il body
  body = {
    roomID : room,
    deviceID: device_id,
    field: fields
  };
  // faccio la richiesta PUT 
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });

}

// *******************************PUT USERS********************************************
// add a room /catalog/User_ID/add_asigned_rooms 
function sendUserRoomsAddPUTrequest(){
  // leggo i campi della form
  userID = $("#user_id").val();
  roomID = $("#rooms").val();
  command = 'add_assigned_rooms';
  // se ci sono più stanze le separo dal '-'
  rooms = [];    
    if (roomID.search("-") != -1){
      rooms = roomID.split("-");    
    }else{rooms = [roomID]}
  // costruisco il body
  body = {
    roomIDs : rooms,
    userID: userID
  };
  // faccio la richiesta PUT
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
  // leggo i campi dalla form
  userID = $("#user_id").val();
  roomID = $("#rooms").val();
  command = 'delete_assigned_rooms';
  // se sono più di una si separano dal '-'
  rooms = [];    
    if (roomID.search("-") != -1){
      rooms = roomID.split("-");    
    }else{rooms = [roomID]}
  // costruzione del body
  body = {
    roomIDs : rooms,
    userID: userID
  };
  // richiesta PUT
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
  // leggo i campi dalla form
  olduserID = $("#old_user_id").val();
  userID = $("#new_user_id").val();
  command = 'change_role';
  // costruzione del body
  body = {
    olduserID : olduserID,
    userID: userID
  };
  // richiesta PUT 
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}
//*************************DELETE FUNCTIONS**************************
// delete devices
function sendDeviceDeleteRequest(){
  // leggo i campi dalla form
  roomID = $("#id_room").val();
  deviceID = $("#id_device").val();
  command = 'delete_device';
  // costruisco il body
  body = {
    roomID : roomID,
    deviceID: deviceID
  };
  // richiesta PUT
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
}
// delete users
function sendUserDeleteRequest(){
  userID = $("#id_user").val();
  command = 'delete_user';
// leggo il body
  body = {
    userID : userID
  };
// invio richiesta
  $.ajax({
    type: "PUT",
    url: "/",
    contentType: "application/json",
    data: JSON.stringify({command: command, body:body}),
    dataType: "json",
  });
  
}
// delete rooms
function sendRoomDeleteRequest(){
  roomID = $("#id1_room").val();
  command = 'delete_room';
  // costruisco il body
  body = {
    roomID : roomID
  };
  // invio richiesta
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
