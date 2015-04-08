module.exports = function(grunt) {

  grunt.initConfig({
    bower: {
        install: { 
            options: {
                targetDir: './static/lib'
            }
        }
    },
    jshint: {
      pkg: grunt.file.readJSON('package.json'),
      files: ['Gruntfile.js', 'static/controllers.js'],
      options: {
        globals: {
          jQuery: true
        }
      }
    },
    watch: {
      files: ['<%= jshint.files %>'],
      tasks: ['jshint']
    }
  });

  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-bower-task');

  grunt.registerTask('default', ['jshint', 'bower:install']);

};
