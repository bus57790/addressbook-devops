pipeline {
    agent any

    environment {
        APP_NAME   = "addressbook-web"
        IMAGE_NAME = "local/addressbook-web"
        PATH       = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/bus57790/addressbook-devops.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube-Server') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${env.APP_NAME} \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=**/*.html
                        """
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                // Using single quotes avoids Groovy variable interpolation character bugs
                sh 'docker build -t local/addressbook-web:${BUILD_NUMBER} .'
            }
        }

        stage('Deploy to Local Server') {
            steps {
                sh 'docker compose down || docker-compose down || true'
                sh 'docker compose up -d --build || docker-compose up -d --build'
            }
        }
    }

    post {
        failure {
            withCredentials([string(credentialsId: 'slack-webhook-url', variable: 'SLACK_URL')]) {
                script {
                    // Safe native string building without plugins
                    def jsonText = '{"text":"❌ Jenkins Pipeline Failed: ' + env.JOB_NAME + ' [Build #' + env.BUILD_NUMBER + '] failed."}'
                    
                    // Native writeFile step present in core Jenkins
                    writeFile file: 'slack.json', text: jsonText
                    
                    sh 'curl -X POST -H "Content-Type: application/json" -d @slack.json "$SLACK_URL"'
                }
            }
        }
    }
}
