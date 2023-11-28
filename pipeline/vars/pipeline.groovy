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
            stage('Security Check') {
                steps {
                    sh "safety check -r ${imageName}/requirements.txt --full-report -o text --continue-on-error"
                }
            }
            stage('Package') {
                steps {
                    withCredentials([string(credentialsId: 'ShantiDockerHub', variable: 'TOKEN')]) {
                        sh "docker login -u 'fishfinna' -p '$TOKEN' docker.io"
                        sh "docker build -t fishfinna/${imageName}:latest ${imageName}/."
                        sh "docker push fishfinna/${imageName}:latest"
                    } 
                }
            }
            stage("Deploy") {
                when {
                    expression { params.DEPLOY }
                }
                steps {
                    sshagent(credentials: ['shanti-kafka-ssh']) {
                        sh "ssh -o StrictHostKeyChecking=no azureuser@20.151.78.202 'cd ~/microservices/deployment && docker pull fishfinna/${imageName}:latest && docker-compose up -d'"
                    }
                }
            }
        }
    }
}