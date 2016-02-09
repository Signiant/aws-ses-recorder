module.exports = function(grunt){
  var pkg = grunt.file.readJSON('package.json');

  grunt.initConfig({
    compress: {
      main: {
        options: {
          archive: '../dist/lambda.zip',
        },
        files: [
          {
            src: 'storeSESBounce_lambda.py',
            cwd: '../src',
            expand: true
          }
        ]
      }
    },
    copy: {
      main: {
        files: [
          {expand: true, src: ['../deploy/policy.lam.json'], dest: '../dist/deploy/', filter: 'isFile'}
        ]
      }
    }
  })

  grunt.registerTask('produce-deployment-rules', function(){
    var propertiesReader = require('properties-reader');
    var sourceFiles = grunt.file.expand("../deploy/environments/*");
    sourceFiles.forEach(function(pathToSource){
      var filePathArray = pathToSource.split("/");
      var envName = filePathArray[filePathArray.length - 1].split(".")[0];
      var envProperties = propertiesReader(pathToSource);

      grunt.file.copy("../deploy/lambda.json", '../dist/deploy/environments/' + envName + '.lam.json', {
        process: function(text) {
          text = replaceText(text, envProperties);
          return text;
        }
      });
    });
  });

  function replaceText(text, envProperties){
    var textWithReplacements = text;
    envProperties.each(function(key, value) {
      textWithReplacements = textWithReplacements.replace(new RegExp('##' + key.replace('.', '\.') + '##', 'g'), value);
    });
    return textWithReplacements;
  }

  grunt.loadNpmTasks('grunt-contrib-compress');
  grunt.loadNpmTasks('grunt-contrib-copy');

  grunt.registerTask('default', ['compress', 'copy', 'produce-deployment-rules']);

};
