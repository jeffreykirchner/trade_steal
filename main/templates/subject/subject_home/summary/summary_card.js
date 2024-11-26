send_name: function send_name(){

    app.working = true;
    formData = {name:document.getElementById("id_name").value, 
                student_id:document.getElementById("id_student_id").value,};
    app.send_message("name", {"formData" : formData});
                     
},

/** take result of moving goods
*/
take_name: function take_name(message_data){

    app.clear_main_form_errors();

    if(message_data.value == "success")
    {
        app.session_player.name = message_data.result.name; 
        app.session_player.student_id = message_data.result.student_id;             
        app.working = false;      
    } 
    else
    {
        app.display_errors(message_data.errors);
    }
},

/**
 * post study link
 */
post_session_link: function post_session_link(){

    if(app.session_player.post_experiment_link == '') return;

    location.href = app.session_player.post_experiment_link;
},

/**
 * show the end game modal
 */
show_end_game_modal: function show_end_game_modal(){
    if(this.end_game_modal_visible) return;

    //hide transfer modals
    this.close_move_modal();

    //show endgame modal
    app.end_game_modal.toggle();

    this.end_game_modal_visible = true;
},

/**
  *  hide choice grid modal modal
*/
 hide_end_game_modal: function hide_end_game_modal(){
    this.end_game_modal_visible=false;
},