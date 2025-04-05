function getSelectedText(translateFull) {
  try {
    var doc = DocumentApp.getActiveDocument();
    if (!doc) return { text: "Không tìm thấy tài liệu nào đang mở.", sourceLang: "unknown" };

    var text = "";
    if (translateFull) {
      text = doc.getBody().getText();
      if (text.length > 10000) {
        text = text.substring(0, 10000) + " [Text truncated due to length]";
      }
    } else {
      var selection = doc.getSelection();
      if (selection) {
        var elements = selection.getRangeElements();
        for (var i = 0; i < elements.length; i++) {
          var element = elements[i];
          if (element.getElement().editAsText) {
            var elemText = element.getElement().editAsText();
            var startOffset = element.getStartOffset();
            var endOffset = element.getEndOffsetInclusive();
            if (startOffset !== -1 && endOffset !== -1) {
              text += elemText.getText().substring(startOffset, endOffset + 1);
            } else {
              text += elemText.getText();
            }
          }
        }
        if (text.length > 10000) {
          text = text.substring(0, 10000) + " [Text truncated due to length]";
        }
      } else {
        text = "Hãy highlight text trước.";
      }
    }

    var sourceLang = detectLanguageWithGemini(text);
    Logger.log("Text to translate: " + text + ", Detected language: " + sourceLang);
    return { text: text, sourceLang: sourceLang };
  } catch (e) {
    Logger.log("Error in getSelectedText: " + e.toString());
    return { text: "Lỗi quyền truy cập: " + e.message, sourceLang: "unknown" };
  }
}

function detectLanguageWithGemini(text) {
  var url = 'https://hitrans.onrender.com/detect-language';
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify({ 'text': text }),
    'muteHttpExceptions': true
  };
  try {
    var response = UrlFetchApp.fetch(url, options);
    var result = JSON.parse(response.getContentText());
    Logger.log("Detect response: " + response.getContentText());
    return result.detected_language || "unknown";
  } catch (e) {
    Logger.log("Error detecting language: " + e.toString());
    return "unknown";
  }
}

function onOpen() {
  var ui = DocumentApp.getUi();
  try {
    ui.createMenu('Text Tools')
      .addItem('Mở Sidebar', 'showSidebar')
      .addToUi();
    Logger.log("Menu created successfully");
  } catch (e) {
    Logger.log("Error in onOpen: " + e.toString());
  }
}

function showSidebar() {
  try {
    var html = HtmlService.createHtmlOutputFromFile('Sidebar')
        .setTitle('Text và Dịch')
        .setWidth(300);
    DocumentApp.getUi().showSidebar(html);
    Logger.log("Sidebar opened successfully");
  } catch (e) {
    Logger.log("Error in showSidebar: " + e.toString());
  }
}

function translateText(text, sourceLang, targetLang, model, temperature, style, translateFull) {
  var url = 'https://hitrans.onrender.com/translate';
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify({
      'text': text,
      'source_lang': sourceLang,
      'target_lang': targetLang,
      'model': model,
      'temperature': parseFloat(temperature),
      'style': style,
      'translate_full': translateFull
    }),
    'muteHttpExceptions': true,
    'timeout': 30000
  };
  try {
    var response = UrlFetchApp.fetch(url, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    Logger.log("Translate response: " + responseText);
    if (responseCode !== 200) {
      Logger.log("API Error: " + responseText);
      return "API failed with code " + responseCode + ": " + responseText;
    }
    // API giờ trả text thô, nhưng kiểm tra xem có JSON không
    try {
      var data = JSON.parse(responseText);
      return data.translated_text || responseText;  // Lấy text thô nếu có, hoặc nguyên response
    } catch (e) {
      return responseText;  // Nếu không parse được JSON, trả text thô
    }
  } catch (e) {
    Logger.log("Error translating: " + e.toString());
    return "Lỗi gọi API: " + e.message;
  }
}
