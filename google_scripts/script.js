//settings to edit here
var google_form_id = ""
var google_drive_folder = ''


///CODE
function getPreFillEntriesMap_(id){
  var form = FormApp.openById(id);
  var items = form.getItems();
  var newFormResponse = form.createResponse();
  var itms = [];
  for(var i = 0; i < items.length; i++){
    var response = getDefaultItemResponse_(items[i]);
    if(response){
      newFormResponse.withItemResponse(response);
      if (items[i].getType() == FormApp.ItemType.MULTIPLE_CHOICE || items[i].getType() == FormApp.ItemType.LIST){
        var choice = [];
        if (items[i].getType() == FormApp.ItemType.MULTIPLE_CHOICE){
          for (var g = 0; g < items[i].asMultipleChoiceItem().getChoices().length; g++){
            choice.push(items[i].asMultipleChoiceItem().getChoices()[g].getValue());
        }
      } else if (items[i].getType() == FormApp.ItemType.LIST){
          for (var g = 0; g < items[i].asListItem().getChoices().length; g++){
            choice.push(items[i].asListItem().getChoices()[g].getValue());
          }
        }
        itms.push({
        id: items[i].getId(),
        entry: null,
        title: items[i].getTitle(),
        type: "" + items[i].getType(),
        choices: choice
        });
      }

    else{
      itms.push({
        id: items[i].getId(),
        entry: null,
        title: items[i].getTitle(),
        type: "" + items[i].getType()
      });
    }
  }
  }
  var ens = newFormResponse.toPrefilledUrl().split("&entry.").map(function(s){
    return s.split("=")[0];
  });
  var link = ens.shift().replace('viewform', 'formResponse');

  return [link, form.getTitle(), form.getDescription(),itms.map(function(r, i){
    r.entry = this[i];
    return r;
  }, ens)];
}

function getDefaultItemResponse_(item){
  switch(item.getType()){
    case FormApp.ItemType.TEXT:
      return item.asTextItem().createResponse("1");
      break;
    case FormApp.ItemType.MULTIPLE_CHOICE:
      return item.asMultipleChoiceItem().createResponse(item.asMultipleChoiceItem().getChoices()[0].getValue());
      break;
    case FormApp.ItemType.LIST:
      var ls = []
      /*
      for (var i = 0; i < item.asListItem().getChoices().length; i++){
        ls[i] = item.asListItem().getChoices()[i].getValue()
      }
      */

      return item.asListItem().createResponse(item.asListItem().getChoices()[0].getValue());
      break;
    
    case FormApp.ItemType.PARAGRAPH_TEXT:
      return item.asParagraphTextItem().createResponse("1");
    default:
      return undefined; 
  } 
}

function get_sf_run(){
  var result = getPreFillEntriesMap_(google_form_id)
  return(result);
// @ts-ignore
}


function settings_form_python() {
  var data = get_sf_run()
  var link = data[0]
  var title = data[1]
  var description = data[2]
  var questions = data[3]
  var showing = [title, description]
  var title_all = []
  var type_all = []
  var entry_all = []
  var choice_all = []
  for (var x = 0; x < questions.length; x++) {
    var title = questions[x].title
    var type = questions[x].type
    var entry = questions[x].entry
    if (type == 'LIST' || type == 'MULTIPLE_CHOICE'){
      var choice = questions[x].choices.toString()
      choice = choice.replaceAll(',', '|')
    }
    else{
      var choice = "None"
    }
    title_all.push(title)
    type_all.push(type)
    entry_all.push(entry)
    choice_all.push(choice)

  }
  console.log(choice_all)
  return [showing, title_all, type_all, entry_all, choice_all]
}

function submit_form(array){
  var form_id = google_form_id
  var form = FormApp.openById(form_id);
  items = form.getItems();
  var itemTypeIs = '';
  var thisItem = '';
  var newResponse = form.createResponse();
  for (j=0;j<items.length;j+=1) {
    thisItem = items[j];
    itemTypeIs = thisItem.getType();

    if (itemTypeIs===FormApp.ItemType.IMAGE || itemTypeIs===FormApp.ItemType.PAGE_BREAK || itemTypeIs===FormApp.ItemType.SECTION_HEADER) {
      continue; //quit this loop, and loop again if the form item is an image, page break or section header
    }

    else{
        if (itemTypeIs == FormApp.ItemType.TEXT){
          var textItem = thisItem.asTextItem();
          var itemResponse = textItem.createResponse(array[j]);
        }

        else if (itemTypeIs == FormApp.ItemType.PARAGRAPH_TEXT){
          var textItem = thisItem.asParagraphTextItem();
          var itemResponse = textItem.createResponse(array[j]);
        }

      else if (itemTypeIs == FormApp.ItemType.MULTIPLE_CHOICE){
      var choosingItem = thisItem.asMultipleChoiceItem();
      var itemResponse = choosingItem.createResponse(array[j]);
        }
      else if(itemTypeIs == FormApp.ItemType.LIST){
        var choosingItem = thisItem.asListItem();
        var itemResponse = choosingItem.createResponse(array[j]);
      }
      else{
        continue
      }
      newResponse.withItemResponse(itemResponse);
      //Logger.log('itemResponse: ' + itemResponse.getResponse());
      };
    };
  newResponse.submit();
  return "submitted"

}

function create_sheet_python(name){
  var name = name
  var folderId = google_drive_folder
  var resource = {
    title: name,
    mimeType: MimeType.GOOGLE_SHEETS,
    parents: [{ id: folderId }]
}
  var fileJson = Drive.Files.insert(resource)
  return(fileJson.id)
}

function list_files_python(){
  var folder = DriveApp.getFolderById(google_drive_folder); // I change the folder ID  here 
  var list = [];
  var files = folder.getFiles();
  while (files.hasNext()){
    file = files.next();
    var row = []
    row.push(file.getName(),file.getId())
    list.push(row);
  }
  console.log(list)
  return list
}

function getSheetById(ss, sheetId) {
  var foundSheets = ss.getSheets().filter(sheet => sheet.getSheetId() === sheetId);
  return foundSheets.length ? foundSheets[0] : undefined;
}

function submit_wishes_python(target, array){
  var lists = list_files_python();
    for(var i = 0; i < lists.length; i++){
      list = lists[i]
      if (list[0] == target){
        var sheetActive = SpreadsheetApp.openById(list[1]);
        var ss = getSheetById(sheetActive, 0)
        ss.appendRow(array)
        return "Submitted"
        }
    }
}
