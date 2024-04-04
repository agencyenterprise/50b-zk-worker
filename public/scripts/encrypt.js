import crypto from "crypto";

const plainString = "It's working pretty well!";

// Mocked enclave public key
// const base64EnclavePublicKey =
//  "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUE3OG5DUXZhMTFsZkRWVXAxOUFMZgpZSTJtSkpYQWpDYVNtRUJqSnYxdi9UUE90Ylc1alF0K3ZOMkZqd3QxVXVMU0lRWE9pUDN0M3c1MEhPUXdMMlh3Cks0OVN5Wk1JVGh5dmRNU1NTNVlwNUFrQi9CaDdVNTl1M2FVNTNrbkt5WlJ2Q3Y3eEJkdDJqcThRVkhZdUZLSTQKbXlFMGRLMWlkMkl0eWUyV2MzSVdob0tMUlZjTVprOUFxS1B2NGJ0Y1k3T3JaeEZkK1k3SzBYM1FBSUNMWUwxQQpSTGVaY2ZwTzlrRG1RUTFXYnZoNWFySm85M1RENml6aVIybjhEK3RqSzN6M3pTUFNZSEIwbEhSTFVyOEdJUjBNCi9GOFZBcDRjSVRsSkdIQVp6aEpmWE50bmNUaUZDNGNKblM5cVg3dzR0anpKMUF3ckg3K3JPVXBGTmZWR1NuWWoKeHdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t";
const base64EnclavePublicKey =
  "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUEwRm5hMkl2NFNMYjkzL1JmVUJWeApDZmFvNm1vVWpWa2VQdHRqY0ZGRzM1SnQ4Znl4OFlTR2NIdnZhdkwyd0VHTXZjQjF2UFdWZ3U4dVJ0WnNzS2tBCnFoVVNZT3I1cUpVeDBRM3NFM0QzSlZPTDF1UVRjamRQRXZHdjN0ZDRKVmtqWTUxajNNbUl0dnpSWDUrcytHYUwKRDFZNnJQTU03QnZ5Q1VtRDBpZVg4RyswWldLcEpaK3kvNkY2VDJpT0ttdlBjZnRieERadUpDb01oUThSYXRTZwpETFVxRDNXRGRaWC9ZaFBNWU1FRHR0NWFPNzZkYzhkSFhYMEQyNFNKcnQ0NFQ1b3dOMW05UVA2eTNGaDhXV3hHCmNvQlZFMDd5UEVwVTZZb3ZBK2k1WmFQblF1VjBGQmRwemJhS2h5SHh1cklDZ1ArQmV2MWRVbUhQS1ljV0xjSmQKcXdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t";

const enclavePublicKey = Buffer.from(
  base64EnclavePublicKey,
  "base64url"
).toString("utf-8");

const aes_key = crypto.randomBytes(32);
const aes_iv = crypto.randomBytes(16);
const cipher_aes = crypto.createCipheriv("aes-256-cbc", aes_key, aes_iv);

const data_AESciphered = Buffer.concat([
  cipher_aes.update(Buffer.from(plainString, "utf8")),
  cipher_aes.final(),
]).toString("base64url");

const aes_key_RSAciphered = crypto
  .publicEncrypt(
    {
      key: enclavePublicKey,
      padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
      oaepHash: "sha256",
    },
    aes_key
  )
  .toString("base64url");

console.log(
  `data=${data_AESciphered}&key=${aes_key_RSAciphered}&iv=${aes_iv.toString(
    "base64url"
  )}`
);
