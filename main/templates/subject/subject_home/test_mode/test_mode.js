{%if session.parameter_set.test_mode%}

/**
 * do random self test actions
 */
randomNumber(min, max){
    //return a random number between min and max
    min = Math.ceil(min);
    max = Math.floor(max+1);
    return Math.floor(Math.random() * (max - min) + min);
},

randomString(min_length, max_length){

    s = "";
    r = this.randomNumber(min_length, max_length);

    for(let i=0;i<r;i++)
    {
        v = this.randomNumber(48, 122);
        s += String.fromCharCode(v);
    }

    return s;
},

doTestMode(){
    {%if DEBUG%}
    console.log("Do Test Mode");
    {%endif%}

    if(this.$data.session.started &&
       this.$data.session.parameter_set.test_mode)
    {
        //do chat
        let go = true;

        if(this.end_game_modal_visible)
        {
            if(this.session_player.name == "")
            {
                document.getElementById("id_name").value =  this.randomString(5, 20);
                document.getElementById("id_student_id").value =  this.randomNumber(1000, 10000);

                this.sendName();
            }

            return;
        }

        if(go)
            if(this.chat_text != "")
            {
                this.sendChat()
                go=false;
            }

        //move goods
        if(go)
            if(this.pixi_modal_open)
            {
                this.sendMoveGoods();
                go=false;
            }
        
        //update production
        if(go)
            if(this.production_slider_one != this.session_player.good_one_production_rate)
            {
                this.sendProdution();
                go=false;
            }

        if(go)
            switch (this.randomNumber(1, 3)){
                case 1:
                    this.doTestModeChat();
                    break;
                
                case 2:
                    this.doTestModeMove();
                    break;
                
                case 3:
                    this.doTestModeProductionUpdate();
                    break;
            }
    }

    setTimeout(this.doTestMode, this.randomNumber(1000 , 10000));
},

/**
 * test mode chat
 */
doTestModeChat(){

    this.chat_text = this.randomString(5, 20);
},

/**
 * test mode move
 */
doTestModeMove(){
    let session_player_source = null;
    let source_container = null;

    if(this.randomNumber(1, 2) == 1)
    {
        if(this.session.parameter_set.allow_stealing == "True")
        {
            session_player_source = this.session.session_players[this.randomNumber(0, this.session.session_players.length-1)];        }
        else
        {
            session_player_source = this.findSessionPlayer(this.session_player.id);            
        }

        source_container = session_player_source.fieldContainer;        

        this.transfer_good_one_amount = this.randomNumber(0, session_player_source.good_one_field);
        this.transfer_good_two_amount = this.randomNumber(0, session_player_source.good_two_field);
    }
    else
    {
        if(this.session.parameter_set.allow_stealing == "True")
        {
            session_player_source = this.session.session_players[this.randomNumber(0, this.session.session_players.length-1)];
        }
        else
        {
            session_player_source = this.findSessionPlayer(this.session_player.id);  
        }            

        source_container = session_player_source.houseContainer;

        this.transfer_good_one_amount = this.randomNumber(0, session_player_source.good_one_house);
        this.transfer_good_two_amount = this.randomNumber(0, session_player_source.good_two_house);

        if(this.session.parameter_set.good_count==3)
        {
            this.transfer_good_three_amount = this.randomNumber(0, session_player_source.good_three_house);
        }
    }

    let session_player_target = this.session.session_players[this.randomNumber(0, this.session.session_players.length-1)];
    let target_container = session_player_target.houseContainer;

    this.handleContainerDown(source_container,
                                {data: {global: {x:source_container.x, y:source_container.y}}})
    
    this.handleContainerUp(target_container,
                            {data: {global: {x:target_container.x, y:target_container.y}}})
},

/**
 * test mode update production percentages
 */
doTestModeProductionUpdate(){
    this.production_slider = this.randomNumber(-50, 50)
    this.update_production_slider();
},
{%endif%}