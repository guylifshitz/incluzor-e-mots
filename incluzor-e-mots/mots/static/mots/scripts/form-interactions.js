;(function($) {

    $('.toggle-iframe').click(function() {
      $$ = $(this);
      // var iframe = $$.parent().parent().parent().parent().parent().parent().parent().parent().parent().find("#dict_iframe");
      var iframe = $$.parents(".card").find(".dict-iframe");
      iframe.toggle();
      console.log("SON");
    });

    $(".toggle-dict").click(function () {
      $$ = $(this);
      // var iframe = $$.parent().parent().parent().parent().parent().parent().parent().parent().parent().find("#dict_iframe");
      var iframe = $$.parents(".card").find(".dict-iframe")
      iframe.show();

      // Get the id of the section
      var dict_id = $$.parent().prev().attr("id");
      id_parts = dict_id.split("_")

      // Nom du dictionnaire
      dict = id_parts[id_parts.length-1];

      // Get the word text
      if (id_parts[1] == "dict")
      {
        var singulier = $("#id_masculin_singulier").val();
      }
      else
      {
        var id_num = dict_id.substring(0, dict_id.lastIndexOf("-") + 1);
        var singulier = $("#"+id_num+"singulier").val();
      }      

      if (dict == "cnrtl") {
        iframe.attr("src", "http://www.cnrtl.fr/definition/"+singulier); 
      }
      else if (dict == "larousse"){
        iframe.attr("src", "http://www.larousse.fr/dictionnaires/francais/"+singulier); 
      }
      else if (dict == "wiktionnaire"){
        iframe.attr("src", "https://fr.wiktionary.org/wiki/"+singulier); 
      }
      else if (dict == "littré"){
        // iframe ne marche pas sur ce site
        // iframe.attr("src", "https://www.littre.org/definition/chat"); 
        var win = window.open('https://www.littre.org/definition/'+singulier, '_blank');
      }
      // else if (dict == "reverso"){
      //   // iframe ne marche pas sur ce site
      //   // iframe.attr("src", "https://dictionary.reverso.net/french-definition/chat"); 
      //   var win = window.open('https://dictionary.reverso.net/french-definition/'+singulier, '_blank');
      // }
    });

    $(".get-dict").click(function () {
      $$ = $(this);

      var dict_id = $$.parent().prev().attr("id");
      id_parts = dict_id.split("_")

      // get dict name
      dict = id_parts[id_parts.length-1];

      // Get the word text
      if (id_parts[1] == "dict")
      {
        var singulier = $("#id_masculin_singulier").val();
      }
      else
      {
        var id_num = dict_id.substring(0, dict_id.lastIndexOf("-") + 1);
        var singulier = $("#"+id_num+"singulier").val();
      }      

      $$.parent().prev().val("");

      $.ajax({
          type: "GET",
          url: "http://localhost:5005/mots/dict",
          data: {
              dictionnaire: dict,
              mot: singulier,
          },
          domElement: $$,
          success: function(data) {
              // Debug 
              // // Si aucun résultat
              if(data.erreur != null)
              {
                // TODO show errors
                console.log(data.erreur);
              }

              // // Si on a des resultats, ajouter les resultats au output
              if(data["existe"] != true)
              {
                this.domElement.parent().prev().val("non-existant");
              }
              else
              {
                this.domElement.parent().prev().val("existe");
              }
          },
          error: function(xhr, status, err) {
              console.log(xhr);
              console.log(xhr.responseText);
              alert("Erreur: " +  xhr.responseText);
          }
      });
      return false;      
    });


    $(".card-header").click(function () {
      $$ = $(this);
      $$.next().toggle();
    });


    $(".freq-button").click(function () {
          $$ = $(this);

          $$.parent().prev().val("");

          // Get word
          var field_id = $(this).parent().prev().attr("id");

          var word_type = field_id.split("_")[1];

          var source = field_id.split("_")[2];
          var number = field_id.split("_")[3];

          if (word_type == "fréquence")
          {
            word_type = "masc";
          }
          else
          {
              word_type = word_type.replace("-fréquence", "");
          }
          
          if (word_type == "masc"){
            var mot_sing = $("#id_masculin_singulier").val();
            var mot_plur = $("#id_masculin_pluriel").val();
          }
          else
          {
            var mot_sing = $("#id_" + word_type + "-singulier").val()
            var mot_plur = $("#id_" + word_type + "-pluriel").val();
          }

          if (number == "singulier"){
            var flexion = mot_sing;
          }
          else{
            var flexion = mot_plur;
          }

          // Faire un appel API
          $.ajax({
              type: "GET",
              url: "http://api.incluzor.fr:5005/mots/fréquence",
              data: {
                  q: flexion,
              },
              success: function(data) {
                
                this.domElement = $$;

                  // Si aucun résultat
                  if(data.erreur != null)
                  {
                    // TODO show errors
                    console.log(data.erreur);
                  }

                  // Si on a des resultats, ajouter les resultats au output
                  if(data[source] != null)
                  {
                    this.domElement.parent().prev().val(data[source]);
                  }
              },
              error: function(xhr, status, err) {
                  console.log(xhr);
              }
          });
          return false;
      });


})(jQuery);
