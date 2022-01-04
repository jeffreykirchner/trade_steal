
/**
 * Given the page number return the requested instruction text
 * @param pageNumber : int
 */
getInstructionPage(pageNumber){

    for(i=0;i<this.instruction_pages.length;i++)
    {
        if(this.instruction_pages[i].page_number==pageNumber)
        {
            return this.instruction_pages[i].text_html;
        }
    }

    return "Text not found";
},