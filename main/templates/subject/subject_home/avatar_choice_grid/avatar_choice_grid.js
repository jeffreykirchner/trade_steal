get_grid_image_html(r, c){

    let parameter_set_avatars = this.session.parameter_set.parameter_set_avatars;

    image_id="";

    for(let i=0; i<parameter_set_avatars.length;i++)
    {
        if(parameter_set_avatars[i].grid_location_row == r && parameter_set_avatars[i].grid_location_col == c)
        {
            if( parameter_set_avatars[i].avatar)
                image_id = parameter_set_avatars[i].avatar.file_name.replace(".jpg", "");
            break;
        }
    }

    return `
        <img class="image_grid" id="` + image_id + `" src="/static/img_trans.gif" width="1" height="1">
    `;
},