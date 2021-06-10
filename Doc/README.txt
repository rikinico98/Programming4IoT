Usare un prefisso specifico per tutti gli ID riferiti a una stessa categoria:
- PER GLI UTENTI 		U_/M_   	es. U_03a1132
- PER LE STANZE 	 	R_   	es. R_asd5768
- PER I DEVICE 		D_   	es. D_12asd4

LISTA DI TUTTE LE POSSIBILI RICHIESTE REST DA CONSIDERARE:

CATALOG:
        # GET
        # catalog/msg_broker
        # catalog/
        #
        # catalog/ID_stanza/ID_Device/topic
        # catalog/ID_utente/assigned_rooms
        # catalog/ID_stanza/assigned_product_type
        # catalog/ID_utente/chatID
        # catalog/ID_stanza/users
        # catalog/ID_stanza/measure_type/TIPO_DI_MISURA
        # catalog/ID_stanza/TS_utilities
        # catalog/ID_stanza/ranges

        # POST
        # catalog/ID_stanza/ID_device/new
        # catalog/ID_utente/new
        # catalog/ID_stanza/new
        # PUT
        # catalog/ID_stanza/ID_device/update_name
        # catalog/ID_stanza/ID_device/change_meas_type
        # catalog/ID_stanza/ID_device/add_service_details
        # catalog/ID_stanza/ID_device/change_topic
        # ctalog/ID_stanza/ID_device/update_timestamp
        # catalog/ID_utente/change_chatID
        # catalog/ID_utente/change_role
        # catalog/ID_utente/add_assigned_rooms
        # catalog/ID_stanza/change_product_type
        # catalog/ID_stanza/change_ranges
        # catalog/ID_stanza/TS_channel
        # catalog/ID_stanza/TS_get
        # catalog/ID_stanza/TS_post
        # DELETE
        # catalog/ID_stanza/ID_device/delete
        # catalog/ID_utente/delete
        # catalog/ID_stanza/delete
        # catalog/ID_stanza/ID_device/delete_service_details/TIPO_DI_SERVIZIO
        # catalog/ID_utente/delete_assigned_rooms

####### ERRORS ##########

-----------SERVER---------------
-Il message Broker non è definito nel catalog
(500, "Msg Broker not defined")

-La porta di accesso non è definita nel catalog
(501, "Port not defined")

--La room list è vuota
(508, "Port not defined")

--La user list è vuota
(509, "User list not defined")

-La porta di accesso  è definita in maniera errata  nel catalog, cioè non è un intero
(502, "Port not properly defined")

-L'ID del dell'oggetto da controllare/modificare non è definito
(505, "Device not found")
(506, "Room not found")
(507, "User not found")


-----------CLIENT---------------
-L'ID digitato non è classificato in nessuna delle categorie(utenti U_,stanze R_, devices D_)
(400, "Unexpected command - ID NOT CLASSIFIED ")

-Il comando inserito non è definito 
(401, "Unexpected command - Wrong Command ")

-L'ID del nuovo oggetto inserito è già presente nel catalog
(402, "User NOT UNIQUE ID")
(403, "Device NOT UNIQUE ID")
(404, "Room NOT UNIQUE ID")
