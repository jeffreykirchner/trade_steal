/**
 * get image html
 */
get_grid_image_html: function get_grid_image_html(r, c){

    let parameter_set_avatars = app.session.parameter_set.parameter_set_avatars;
    let parameter_set_avatars_order = app.session.parameter_set.parameter_set_avatars_order;

    image_id="blank.png";

    for(let i=0; i<parameter_set_avatars_order.length;i++)
    {
        let id = parameter_set_avatars_order[i];
        if(parameter_set_avatars[id].grid_location_row == r && parameter_set_avatars[id].grid_location_col == c)
        {
            if( parameter_set_avatars[id].avatar)
                image_id = parameter_set_avatars[id].avatar.file_name;
            break;
        }
    }

    if(image_id == "blank.png")
        return `<img id="` + image_id + `" class="" src="/static/avatars/` + image_id + `">`;

    return `        
        <img class="image_choice_grid img-thumbnail" id="` + image_id + `" src="/static/avatars/` + image_id + `">
    `;
},

/**
 * given a row and column return the avatar from the parameter set
 */
get_grid_avatar: function get_grid_avatar(r, c){
    
    let parameter_set_avatars = app.session.parameter_set.parameter_set_avatars;
    let parameter_set_avatars_order = app.session.parameter_set.parameter_set_avatars_order;

    for(let i=0; i<parameter_set_avatars_order.length;i++)
    {
        let id = parameter_set_avatars_order[i];
        if(parameter_set_avatars[id].grid_location_row == r && parameter_set_avatars[id].grid_location_col == c)
        {
            return parameter_set_avatars[id];
        }
    }

    return null;
},

/**
 * handle choice grid click
 */
take_choice_grid_click: function take_choice_grid_click(r, c){

    if(app.working) return;
    if(app.session_player.avatar != null) return;

    let parameter_set_avatars = app.session.parameter_set.parameter_set_avatars;

    //check for blank
    for(let i=0; i<parameter_set_avatars.length;i++)
    {
        if(parameter_set_avatars[i].grid_location_row == r && 
           parameter_set_avatars[i].grid_location_col == c &&
           parameter_set_avatars[i].avatar == null
           )
        {
            return
        }
    }


    app.avatar_choice_grid_selected_row = r;
    app.avatar_choice_grid_selected_col = c;
},

/**
 * handle choice grid click
 */
 take_choice_grid_label: function take_choice_grid_label(label){

    let parameter_set_avatars = app.session.parameter_set.parameter_set_avatars;

    //check for blank
    for(let i=0; i<parameter_set_avatars.length;i++)
    {

        if(parameter_set_avatars[i].avatar && parameter_set_avatars[i].avatar.label == label)
        {
            app.avatar_choice_grid_selected_row = parameter_set_avatars[i].grid_location_row;
            app.avatar_choice_grid_selected_col = parameter_set_avatars[i].grid_location_col;

            return
        }
    }
},

/**
 * send avatar choice
 */
send_avatar: function send_avatar(){

    if(app.working) return;

    if(app.avatar_choice_grid_selected_row == 0) return;
    if(app.avatar_choice_grid_selected_col == 0) return;

    if(app.session_player.avatar != null) return;
    
    app.working = true;
    app.send_message("avatar", {"row" : app.avatar_choice_grid_selected_row,
                                "col" : app.avatar_choice_grid_selected_col,
                            });             
},

/** take result of moving goods
*/
take_avatar: function take_avatar(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    app.working = false;

    if(message_data.value == "success")
    {
        app.session_player.avatar = message_data.result.avatar;         
    } 
    else
    {
        
    }
},

/**
 * if needed show avatar choice grid
 */
show_avatar_choice_grid: function show_avatar_choice_grid(){

    if((this.session.parameter_set.avatar_assignment_mode == 'Subject Select' || 
        this.session.parameter_set.avatar_assignment_mode == 'Best Match') &&
        this.session.current_experiment_phase == "Selection" &&
        !this.avatar_choice_modal_visible)

    {
        app.avatar_choice_grid_modal.toggle();

        this.avatar_choice_modal_visible=true;

        if(this.session_player.avatar != null)
        {
            this.take_choice_grid_label(this.session_player.avatar.label)
        }
    }
},

/** hide choice grid modal modal
*/
hide_choice_grid_modal: function hide_choice_grid_modal(){
    this.avatar_choice_modal_visible=false;
},


