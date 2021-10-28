
/**
 * update the pixi players with new info
 */
updatePixiPlayers(){
   
},

/**
 * setup pixi players
 */
setupPixiPlayers(){

    PIXI.utils.destroyTextureCache();


    // Create the sprite and add it to the stage
    app.$data.sprite = PIXI.Sprite.from('/static/houseYou.bmp');
    app.$data.pixi_app.stage.addChild(app.$data.sprite);
   
},

getLocationCordinates(index){

    

};