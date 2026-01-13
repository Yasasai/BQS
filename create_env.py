with open('.env', 'w') as f:
    f.write("ORACLE_USER=yasasvi.upadrasta@inspiraenterprise.com\n")
    f.write("ORACLE_PASS=Welcome@123\n")
    f.write("ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com\n")
    f.write("ORACLE_TOKEN_URL=\n")
    f.write("ORACLE_CLIENT_ID=\n")
    f.write("ORACLE_CLIENT_SECRET=\n")
    f.write("ORACLE_SCOPE=https://eijs-test.fa.em2.oraclecloud.com:443/crmRestApi/resources/latest/\n")
print("Successfully created .env file")
