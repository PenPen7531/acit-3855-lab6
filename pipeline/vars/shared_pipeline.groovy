def call(image) {
    pipeline {
        agent any

        // Deploy parameter
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name:'DEPLOY')
        }

        stages {
            
            // Checks python code with lint. Fails under score of 5
            stage('Lint') {
                steps {
                    sh "pip install -r ${image}/requirements.txt --break-system-packages"
                    sh "pylint --fail-under=5.0 ${image}/*.py"
                }
            }

            // Scans for vulnerabilities in requirements.txt
            // DOCS: https://pypi.org/project/safety/ 

            stage ('Security Check'){
                steps{
                    sh "safety check -r ${image}/requirements.txt --full-report -o text --continue-on-error"
                    
                }
            }

            // Packages image and pushes to dockerhub
            stage('Package') {
                steps {
                    withCredentials([string(credentialsId: 'Docker-Assignment-Token', variable: 'TOKEN')]) {
                        sh "docker login -u 'penpen7531' -p '$TOKEN' docker.io"
                        sh "docker build -t penpen7531/${image}:latest ${image}/."
                        sh "docker push penpen7531/${image}:latest"
                        sh "echo Package Completed"
                    } 
                }
            }

            // Deploy application from 3855 VM 
            stage('Deploy'){

                // Only run when deploy param is checked
                when {
                        expression { params.DEPLOY }
                }

                // Use SSH credentials for key
                steps {
                    sshagent(credentials: ['SSH']) {
                        sh "ssh -o StrictHostKeyChecking=no -l azureuser 172.178.11.14 'cd ~/acit-3855-lab6/deployment && docker pull penpen7531/${image}:latest && docker-compose up -d'"
                    }   
                }
            }
        }
    }
}