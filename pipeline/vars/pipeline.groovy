def call(imageName) {
    pipeline {
        agent any
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }
        stages {
            stage('test'){
                steps{
                    sh "echo hello world"
                }
            }
            stage('Lint') {
                steps {
                    sh "pip install -r ${imageName}/requirements.txt --break-system-packages"
                    sh "pylint --fail-under=5.0 ${imageName}/*.py"
                }
            }
            
        }
    }
}