/** show transfer modal when mouse up on valid target
*/
showTransferModal: function showTransferModal(container){

    if(app.pixi_modal_open) return;

    if(!pixi_transfer_line.visible ||
       container ==  pixi_transfer_source ||
       pixi_transfer_source == null ||
       pixi_transfer_target == null)
    {
        app.turnOffHighlights();
        return;
    } 

    parameter_set = app.session.parameter_set;

    app.transfer_source_modal_string = pixi_transfer_source.name.modal_label;
    app.transfer_target_modal_string = pixi_transfer_target.name.modal_label;

    app.transfer_modal_good_one_rgb = pixi_transfer_source.name.good_one_color;
    app.transfer_modal_good_two_rgb = pixi_transfer_source.name.good_two_color;

    app.transfer_modal_good_one_name = pixi_transfer_source.name.good_a_label;
    app.transfer_modal_good_two_name = pixi_transfer_source.name.good_b_label;

    app.pixi_modal_open = true;
    app.cancel_modal=true;

    if(parameter_set.good_count == 2 || pixi_transfer_source.name.type == "field")
    {
        app.moveTwoGoodsModal.toggle();
    }
    else
    {
        app.transfer_modal_good_three_rgb = pixi_transfer_source.name.good_three_color;
        app.transfer_modal_good_three_name = pixi_transfer_source.name.good_c_label;

        app.moveThreeGoodsModal.toggle();
    }
},

/** hide transfer modal
*/
hideTransferModal:function hideTransferModal(){
    
    app.clear_main_form_errors();

    if(app.cancel_modal)
    {
       app.transfer_good_one_amount = 0;
       app.transfer_good_two_amount = 0;
       app.transfer_good_three_amount = 0;
    }

    app.pixi_modal_open = false;
    app.turnOffHighlights();
},

sendMoveGoods: function sendMoveGoods(){
    
    if(app.working == true) return;
    if(!pixi_transfer_source) return;
    if(!pixi_transfer_target) return; 

    app.clear_main_form_errors();

    if(pixi_transfer_source.name.type == "house" &&
       app.session.parameter_set.good_count == 3)
    {
        if(app.transfer_good_one_amount == 0 && 
           app.transfer_good_two_amount == 0 &&
           app.transfer_good_three_amount == 0)
        {
            let errors = {transfer_good_one_amount_3g:["Invalid entry."]};
            app.display_errors(errors);
            return;
        }

        var form_data = {transfer_good_one_amount_3g: app.transfer_good_one_amount,
                         transfer_good_two_amount_3g: app.transfer_good_two_amount,
                         transfer_good_three_amount_3g: app.transfer_good_three_amount};
    }
    else
    {
         if(app.transfer_good_one_amount == 0 && 
            app.transfer_good_two_amount == 0)
         {
            if(app.test_mode)
            {
                app.closeMoveModal();
            }

            let errors = {transfer_good_one_amount_2g:["Invalid entry."]};
            app.display_errors(errors);
            return;
         }

        var form_data = {transfer_good_one_amount_2g: app.transfer_good_one_amount,
                         transfer_good_two_amount_2g: app.transfer_good_two_amount};
    }

    app.working = true;
    app.send_message("move_goods",
                     {"sourceType" : pixi_transfer_source.name.type.toString(),
                      "sourceID" :  pixi_transfer_source.name.user_id.toString(),

                      "targetType" : pixi_transfer_target.name.type.toString(),
                      "targetID" : pixi_transfer_target.name.user_id.toString(),

                      "formData" : form_data,},
                    "group");
},

/** take result of moving goods
*/
takeMoveGoods: function takeMoveGoods(message_data){
    //app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.value == "success")
    {
        app.take_update_goods(message_data);    
        app.closeMoveModal();               
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.errors);
    }
},

/**
 * close and reset the move modals
 */
closeMoveModal: function closeMoveModal(){
    app.moveTwoGoodsModal.hide();
    app.moveThreeGoodsModal.hide();

    app.transfer_good_one_amount = 0;  
    app.transfer_good_two_amount = 0;  
    app.transfer_good_three_amount = 0;
},

/** take updated data from goods being moved by another player
*    @param message_data {json} session day in json format
*/
takeUpdateMoveGoods: function takeUpdateMoveGoods(message_data){


    if(message_data.value == "success")
    {
        app.take_update_goods(message_data);    

        if(parseInt(message_data.session_player_id) == app.session_player.id)
        {
            app.closeMoveModal();    
            app.working = false;           
        }
    } 
    else
    {
        if(parseInt(message_data.session_player_id) == app.session_player.id)
        {
            app.cancel_modal=true;                           
            app.display_errors(message_data.errors);
            app.working = false;

            if(app.test_mode)
            {
                app.closeMoveModal();
            }
        }
    }
},

/** update good counts of players in list
*    @param message_data {json} session day in json format
*/
take_update_goods: function take_update_goods(message_data){
    results = message_data.result;

    let session_player = app.session_player;

    for(let r=0; r<results.length; r++){
        player_id = results[r].id;
        
        //update session player
        if(app.is_subject)
        {
            if(player_id == session_player.id)
            {
                session_player.good_one_house = results[r].good_one_house;
                session_player.good_two_house = results[r].good_two_house;
                session_player.good_three_house = results[r].good_three_house;

                session_player.good_one_field = results[r].good_one_field;
                session_player.good_two_field = results[r].good_two_field; 

                if(results[r].notice)
                {
                    session_player.notices.push(results[r].notice);

                    //scroll to view
                    if(session_player.notices.length>0)
                    {
                        Vue.nextTick(() => {app.update_notice_displayScroll()});        
                    }
                }
            }
        }

        player = app.find_session_player(player_id);

        if(player)
        {
            player.good_one_house = results[r].good_one_house;
            player.good_two_house = results[r].good_two_house;
            player.good_three_house = results[r].good_three_house;

            player.good_one_field = results[r].good_one_field;
            player.good_two_field = results[r].good_two_field;               

            player_index = app.find_session_playerIndex(player_id);

            app.setupSingleHouse(player_index);
            app.setupSingleField(player_index);
        }        
    }

    if(app.is_subject) app.calc_waste();
},

/**
 * scroll notice text to the bottom
 */
update_notice_displayScroll: function update_notice_displayScroll(){
    // if(app.session_player.notices.length==0) return;

    // var elmnt = document.getElementById("notice_id_" + app.session_player.notices[app.session_player.notices.length-1].id.toString());
    // elmnt.scrollIntoView(); 
},
