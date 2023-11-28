def call(imageName) {
    pipeline {
        agent any
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }
        stages {
        
            stage('Lint') {
                steps {
                    sh "pip install -r ${imageName}/requirements.txt --break-system-packages"
                    sh "pylint --fail-under=5.0 ${imageName}/*.py"
                }
            }
            stage('Package') {
                steps {
                    withCredentials([string(credentialsId: 'Jwang-Dockerhub', variable: 'TOKEN')]) {
                        sh "docker login -u 'penpen7531' -p '$TOKEN' docker.io"
                        sh "docker build -t penpen7531/${imageName}:latest ${imageName}/."
                        sh "docker push penpen7531/${imageName}:latest"
                    } 
                }
            }

            stage('Deploy'){
                steps{
                sshagent(credentials: ['SSH']) {
                
                sh "ssh -o StrictHostKeyChecking=no azureuser@172.178.11.14 'cd ~/acit-3855-lab6/deployment && docker pull penpen7531/${imageName}:latest && docker-compose up -d'"
                
                 }   
            }
            }
        }
    }
}