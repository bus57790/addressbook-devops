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
                git branch: 'feature/testing', url: 'https://github.com/bus57790/addressbook-devops.git'
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
                sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh "trivy image --severity HIGH,CRITICAL --exit-code 1 ${IMAGE_NAME}:${BUILD_NUMBER}"
            }
        }

        stage('Deploy to Local Server') {
            steps {
                sh 'docker compose down -v || docker-compose down -v || true'
                sh 'docker compose up -d --build || docker-compose up -d --build'
            }
        }

        stage('Seed Sample Users') {
            steps {
                script {
                    sh 'sleep 5' // Brief delay for Postgres container ready check
                    sh '''
                        docker exec -i addressbook_db psql -U postgres -d addressbook <<EOF
                        INSERT INTO contacts (full_name, phone, email, address) VALUES
                        ('Ada Lovelace', '+1-555-0101', 'ada@example.com', '10 Binary Way, London, UK'),
                        ('Alan Turing', '+1-555-0102', 'alan@example.com', '42 Enigma Ave, Bletchley, UK'),
                        ('Grace Hopper', '+1-555-0103', 'grace@example.com', '1952 Compiler Rd, Arlington, VA'),
                        ('Linus Torvalds', '+1-555-0104', 'linus@example.com', '100 Linux Blvd, Portland, OR')
                        ON CONFLICT DO NOTHING;
EOF
                    '''
                }
            }
        }

        stage('Generate & Archive QR Artifacts') {
            steps {
                script {
                    sh "docker exec addressbook_web python generate_qr_codes.py"
                    sh "docker cp addressbook_web:/app/sample_qr_codes ./sample_qr_codes"
                    archiveArtifacts artifacts: 'sample_qr_codes/*.png', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }

        success {
            withCredentials([
                string(credentialsId: 'slack-webhook-url', variable: 'SLACK_URL'),
                string(credentialsId: 'twilio-sid', variable: 'TWILIO_SID'),
                string(credentialsId: 'twilio-token', variable: 'TWILIO_TOKEN'),
                string(credentialsId: 'twilio-from', variable: 'TWILIO_FROM'),
                string(credentialsId: 'notification-to', variable: 'NOTIFICATION_TO')
            ]) {
                script {
                    // Slack Success Notification
                    def jsonText = "{\"text\":\"✅ Pipeline Succeeded: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] - Deployed, Seeded, and QR Artifacts Generated.\"}"
                    writeFile file: 'slack.json', text: jsonText
                    sh 'curl -s -X POST -H "Content-Type: application/json" -d @slack.json "$SLACK_URL"'

                    // SMS Success Notification (Twilio)
                    sh '''
                        curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \
                        --data-urlencode "From=${TWILIO_FROM}" \
                        --data-urlencode "To=${NOTIFICATION_TO}" \
                        --data-urlencode "Body=✅ Pipeline Succeeded: ${JOB_NAME} [Build #${BUILD_NUMBER}] deployed." \
                        -u "${TWILIO_SID}:${TWILIO_TOKEN}"
                    '''
                }
            }
        }

        failure {
            withCredentials([
                string(credentialsId: 'slack-webhook-url', variable: 'SLACK_URL'),
                string(credentialsId: 'twilio-sid', variable: 'TWILIO_SID'),
                string(credentialsId: 'twilio-token', variable: 'TWILIO_TOKEN'),
                string(credentialsId: 'twilio-from', variable: 'TWILIO_FROM'),
                string(credentialsId: 'notification-to', variable: 'NOTIFICATION_TO')
            ]) {
                script {
                    // Slack Failure Notification
                    def jsonText = "{\"text\":\"❌ Pipeline Failed: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}]\"}"
                    writeFile file: 'slack.json', text: jsonText
                    sh 'curl -s -X POST -H "Content-Type: application/json" -d @slack.json "$SLACK_URL"'

                    // SMS Failure Notification (Twilio)
                    sh '''
                        curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \
                        --data-urlencode "From=${TWILIO_FROM}" \
                        --data-urlencode "To=${NOTIFICATION_TO}" \
                        --data-urlencode "Body=❌ Pipeline Failed: ${JOB_NAME} [Build #${BUILD_NUMBER}]" \
                        -u "${TWILIO_SID}:${TWILIO_TOKEN}"
                    '''
                }
            }
        }
    }
}
