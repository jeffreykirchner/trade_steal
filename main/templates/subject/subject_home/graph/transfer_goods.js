/** show transfer modal when mouse up on valid target
*/
showTransferModal(container){

    if(app.pixi_modal_open) return;

    if(!app.$data.pixi_transfer_line.visible ||
       container ==  app.$data.pixi_transfer_source ||
       app.$data.pixi_transfer_source == null ||
       app.$data.pixi_transfer_target == null)
    {
        app.turnOffHighlights();
        return;
    } 

    parameter_set = app.$data.session.parameter_set;

    app.$data.transfer_source_modal_string = app.$data.pixi_transfer_source.name.modal_label;
    app.$data.transfer_target_modal_string = app.$data.pixi_transfer_target.name.modal_label;

    app.$data.transfer_modal_good_one_rgb = app.$data.pixi_transfer_source.name.good_one_color;
    app.$data.transfer_modal_good_two_rgb = app.$data.pixi_transfer_source.name.good_two_color;

    app.$data.transfer_modal_good_one_name = app.$data.pixi_transfer_source.name.good_a_label;
    app.$data.transfer_modal_good_two_name = app.$data.pixi_transfer_source.name.good_b_label;

    app.$data.pixi_modal_open = true;
    app.$data.cancelModal=true;

    if(parameter_set.good_count == 2 || app.$data.pixi_transfer_source.name.type == "field")
    {
        var myModal = new bootstrap.Modal(document.getElementById('moveTwoGoodsModal'), {
            keyboard: false
            })
    }
    else
    {
        app.$data.transfer_modal_good_three_rgb = app.$data.pixi_transfer_source.name.good_three_color;
        app.$data.transfer_modal_good_three_name = app.$data.pixi_transfer_source.name.good_c_label;

        var myModal = new bootstrap.Modal(document.getElementById('moveThreeGoodsModal'), {
            keyboard: false
            })
    }

    myModal.toggle();
},

/** hide transfer modal
*/
hideTransferModal:function(){
    
    app.clearMainFormErrors();

    if(app.$data.cancelModal)
    {
       app.$data.transfer_good_one_amount = 0;
       app.$data.transfer_good_two_amount = 0;
       app.$data.transfer_good_three_amount = 0;
    }

    app.$data.pixi_modal_open = false;
    app.turnOffHighlights();
},

sendMoveGoods(){
    
    if(app.$data.working == true) return;
    if(!app.$data.pixi_transfer_source) return;
    if(!app.$data.pixi_transfer_target) return; 

    if(app.$data.pixi_transfer_source.name.type == "house" &&
       app.$data.session.parameter_set.good_count == 3)
    {
        form_data = $("#moveThreeGoodsForm").serializeArray();
    }
    else
    {
        form_data = $("#moveTwoGoodsForm").serializeArray();
    }

    app.$data.working = true;
    app.sendMessage("move_goods", {"sourceType" : app.$data.pixi_transfer_source.name.type.toString(),
                                   "sourceID" : app.$data.pixi_transfer_source.name.user_id.toString(),

                                   "targetType" : app.$data.pixi_transfer_target.name.type.toString(),
                                   "targetID" : app.$data.pixi_transfer_target.name.user_id.toString(),

                                   "formData" : form_data,});
},

/** take result of moving goods
*/
takeMoveGoods(messageData){
    //app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeUpdateGoods(messageData);       
        $('#moveTwoGoodsModal').modal('hide');
        $('#moveThreeGoodsModal').modal('hide');


        app.$data.transfer_good_one_amount = 0;  
        app.$data.transfer_good_two_amount = 0;  
        app.$data.transfer_good_three_amount = 0;            
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    }
},

/** take updated data from goods being moved by another player
*    @param messageData {json} session day in json format
*/
takeUpdateMoveGoods(messageData){
    app.takeUpdateGoods(messageData);
},

/** update good counts of players in list
*    @param messageData {json} session day in json format
*/
takeUpdateGoods(messageData){
    results = messageData.status.result;

    for(let r=0; r<results.length; r++){
        player_id = results[r].id;

        for(let p=0; p<app.$data.session.session_players.length; p++)
        {
            player = app.$data.session.session_players[p];

            if(player.id == player_id)
            {
                player.good_one_house = results[r].good_one_house;
                player.good_two_house = results[r].good_two_house;
                player.good_three_house = results[r].good_three_house;

                player.good_one_field = results[r].good_one_field;
                player.good_two_field = results[r].good_two_field;               

                player.houseContainer.destroy();
                player.fieldContainer.destroy();

                app.setupSingleHouse(p);
                app.setupSingleField(p);

                break;
            }
        }
    }
},
