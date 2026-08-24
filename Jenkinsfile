pipeline {
    agent any

    environment {
        APP_NAME   = "addressbook-web"
        IMAGE_NAME = "local/addressbook-web"
        PATH       = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"
    }

    stages {

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube-Server') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${env.APP_NAME} \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=**/*.html \
                            -Dsonar.python.version=3.11
                        """
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build \
                      -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                      -t ${IMAGE_NAME}:latest \
                      .
                """
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh """
                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --scanners vuln \
                      --exit-code 0 \
                      ${IMAGE_NAME}:${BUILD_NUMBER}
                """
            }
        }

        stage('Validate Compose') {
            steps {
                sh '''
                    docker compose config --quiet
                '''
            }
        }

        stage('Deploy to Local Server') {
            steps {
                sh '''
                    set -e

                    echo "Stopping previous deployment..."
                    docker compose down || true

                    echo "Starting application..."
                    docker compose up -d --build

                    echo "Container status:"
                    docker compose ps
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "Waiting for services..."
                    sleep 5

                    docker compose ps

                    echo "Checking database health..."
                    docker inspect \
                      --format='{{.State.Health.Status}}' \
                      addressbook_db

                    echo "Testing web application..."
                    curl --fail \
                      --retry 10 \
                      --retry-delay 3 \
                      http://192.168.1.184:5000/
                '''
            }
        }

        stage('Seed Sample Users') {
            steps {
                sh '''
                    docker exec -i addressbook_db \
                      psql -U postgres -d addressbook <<'EOF'
INSERT INTO contacts
    (full_name, phone, email, address)
VALUES
    ('Ada Lovelace',
     '+1-555-0101',
     'ada@example.com',
     '10 Binary Way, London, UK'),

    ('Alan Turing',
     '+1-555-0102',
     'alan@example.com',
     '42 Enigma Ave, Bletchley, UK'),

    ('Grace Hopper',
     '+1-555-0103',
     'grace@example.com',
     '1952 Compiler Rd, Arlington, VA'),

    ('Linus Torvalds',
     '+1-555-0104',
     'linus@example.com',
     '100 Linux Blvd, Portland, OR')
ON CONFLICT DO NOTHING;
EOF
                '''
            }
        }

        stage('Generate & Archive QR Artifacts') {
            steps {
                sh '''
                    rm -rf sample_qr_codes

                    docker exec \
                      addressbook_web \
                      python generate_qr_codes.py

                    docker cp \
                      addressbook_web:/app/sample_qr_codes \
                      ./sample_qr_codes
                '''

                archiveArtifacts(
                    artifacts: 'sample_qr_codes/*.png',
                    fingerprint: true
                )
            }
        }
    }

    post {

        success {
            withCredentials([
                string(
                    credentialsId: 'slack-webhook-url',
                    variable: 'SLACK_URL'
                ),
                string(
                    credentialsId: 'twilio-sid',
                    variable: 'TWILIO_SID'
                ),
                string(
                    credentialsId: 'twilio-token',
                    variable: 'TWILIO_TOKEN'
                ),
                string(
                    credentialsId: 'twilio-from',
                    variable: 'TWILIO_FROM'
                ),
                string(
                    credentialsId: 'notification-to',
                    variable: 'NOTIFICATION_TO'
                )
            ]) {
                script {

                    def jsonText =
                        """{"text":"Pipeline Succeeded: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] - Deployed, Seeded, and QR Artifacts Generated."}"""

                    writeFile(
                        file: 'slack.json',
                        text: jsonText
                    )

                    sh '''
                        curl --fail-with-body \
                          -sS \
                          -X POST \
                          -H 'Content-Type: application/json' \
                          --data @slack.json \
                          "$SLACK_URL" \
                          || echo "WARNING: Slack notification failed"
                    '''

                    sh '''
                        curl --fail-with-body \
                          -sS \
                          -X POST \
                          "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \
                          --data-urlencode "From=${TWILIO_FROM}" \
                          --data-urlencode "To=${NOTIFICATION_TO}" \
                          --data-urlencode "Body=Jenkins Build #${BUILD_NUMBER} for ${JOB_NAME} SUCCEEDED. Deployment and seeding complete." \
                          -u "${TWILIO_SID}:${TWILIO_TOKEN}" \
                          || echo "WARNING: Twilio notification failed"
                    '''
                }
            }
        }

        failure {
            withCredentials([
                string(
                    credentialsId: 'slack-webhook-url',
                    variable: 'SLACK_URL'
                ),
                string(
                    credentialsId: 'twilio-sid',
                    variable: 'TWILIO_SID'
                ),
                string(
                    credentialsId: 'twilio-token',
                    variable: 'TWILIO_TOKEN'
                ),
                string(
                    credentialsId: 'twilio-from',
                    variable: 'TWILIO_FROM'
                ),
                string(
                    credentialsId: 'notification-to',
                    variable: 'NOTIFICATION_TO'
                )
            ]) {
                script {

                    def jsonText =
                        """{"text":"Pipeline Failed: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}]"}"""

                    writeFile(
                        file: 'slack.json',
                        text: jsonText
                    )

                    sh '''
                        curl --fail-with-body \
                          -sS \
                          -X POST \
                          -H 'Content-Type: application/json' \
                          --data @slack.json \
                          "$SLACK_URL" \
                          || echo "WARNING: Slack notification failed"
                    '''

                    sh '''
                        curl --fail-with-body \
                          -sS \
                          -X POST \
                          "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \
                          --data-urlencode "From=${TWILIO_FROM}" \
                          --data-urlencode "To=${NOTIFICATION_TO}" \
                          --data-urlencode "Body=Jenkins Build #${BUILD_NUMBER} for ${JOB_NAME} FAILED. Check Jenkins console log." \
                          -u "${TWILIO_SID}:${TWILIO_TOKEN}" \
                          || echo "WARNING: Twilio notification failed"
                    '''
                }
            }
        }

        always {
            cleanWs()
        }
    }
}
