{% load static %}

{%include "subject/subject_home/graph/pixi_setup.js"%}
{%include "subject/subject_home/graph/pixi_interface.js"%}
{%include "subject/subject_home/graph/transfer_goods.js"%}

/**
 * set the visibility of all feilds and houses
 */
set_field_house_visbility: function set_field_house_visbility(value){
    
    for(let i=0;i<app.session.session_players_order.length;i++)
    {
        if(house_containers[i])
        {
            house_containers[i].visible = value;
        }

        if(field_containers[i])
        {
            field_containers[i].visible = value;
        }

        if(avatar_containers[i])
        {
            avatar_containers[i].visible = value;
        }
    }
},

