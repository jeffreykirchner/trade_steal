/** show transfer modal when mouse up on valid target
*/
showTransferModal(container){

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
    app.cancelModal=true;

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
hideTransferModal:function(){
    
    app.clearMainFormErrors();

    if(app.cancelModal)
    {
       app.transfer_good_one_amount = 0;
       app.transfer_good_two_amount = 0;
       app.transfer_good_three_amount = 0;
    }

    app.pixi_modal_open = false;
    app.turnOffHighlights();
},

sendMoveGoods(){
    
    if(this.working == true) return;
    if(!pixi_transfer_source) return;
    if(!pixi_transfer_target) return; 

    app.clearMainFormErrors();

    if(pixi_transfer_source.name.type == "house" &&
       this.session.parameter_set.good_count == 3)
    {
        if(this.transfer_good_one_amount == 0 && 
           this.transfer_good_two_amount == 0 &&
           this.transfer_good_three_amount == 0)
        {
            let errors = {transfer_good_one_amount_3g:["Invalid Entry."]};
            this.displayErrors(errors);
            return;
        }

        var form_data = {transfer_good_one_amount_3g: this.transfer_good_one_amount,
                         transfer_good_two_amount_3g: this.transfer_good_two_amount,
                         transfer_good_three_amount_3g: this.transfer_good_three_amount};
    }
    else
    {
         if(this.transfer_good_one_amount == 0 && 
            this.transfer_good_two_amount == 0)
         {
             let errors = {transfer_good_one_amount_2g:["Invalid Entry."]};
             this.displayErrors(errors);
             return;
         }

        var form_data = {transfer_good_one_amount_2g: this.transfer_good_one_amount,
                         transfer_good_two_amount_2g: this.transfer_good_two_amount};
    }

    this.working = true;
    app.sendMessage("move_goods", {"sourceType" : pixi_transfer_source.name.type.toString(),
                                   "sourceID" :  pixi_transfer_source.name.user_id.toString(),

                                   "targetType" : pixi_transfer_target.name.type.toString(),
                                   "targetID" : pixi_transfer_target.name.user_id.toString(),

                                   "formData" : form_data,});
},

/** take result of moving goods
*/
takeMoveGoods(messageData){
    //app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeUpdateGoods(messageData);    
        this.closeMoveModal();               
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    }
},

/**
 * close and reset the move modals
 */
closeMoveModal(){
    app.moveTwoGoodsModal.hide();
    app.moveThreeGoodsModal.hide();

    this.transfer_good_one_amount = 0;  
    this.transfer_good_two_amount = 0;  
    this.transfer_good_three_amount = 0;
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

    let session_player = this.session_player;

    for(let r=0; r<results.length; r++){
        player_id = results[r].id;
        
        //update session player
        if(this.is_subject)
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
                        Vue.nextTick(() => {app.updateNoticeDisplayScroll()});        
                    }
                }
            }
        }

        player = this.findSessionPlayer(player_id);

        if(player)
        {
            player.good_one_house = results[r].good_one_house;
            player.good_two_house = results[r].good_two_house;
            player.good_three_house = results[r].good_three_house;

            player.good_one_field = results[r].good_one_field;
            player.good_two_field = results[r].good_two_field;               

            player_index = this.findSessionPlayerIndex(player_id);

            app.setupSingleHouse(player_index);
            app.setupSingleField(player_index);
        }        
    }

    if(this.is_subject) app.calcWaste();
},

/**
 * scroll notice text to the bottom
 */
updateNoticeDisplayScroll(){
    // if(this.session_player.notices.length==0) return;

    // var elmnt = document.getElementById("notice_id_" + app.session_player.notices[app.session_player.notices.length-1].id.toString());
    // elmnt.scrollIntoView(); 
},
