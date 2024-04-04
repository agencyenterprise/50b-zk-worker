import crypto from "crypto";

const script = "my_zk_circuit_script";
const inputs = '{ "a": 1, "b": 2 }';

// Mocked enclave public key
// const base64EnclavePublicKey =
//   "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUE3OG5DUXZhMTFsZkRWVXAxOUFMZgpZSTJtSkpYQWpDYVNtRUJqSnYxdi9UUE90Ylc1alF0K3ZOMkZqd3QxVXVMU0lRWE9pUDN0M3c1MEhPUXdMMlh3Cks0OVN5Wk1JVGh5dmRNU1NTNVlwNUFrQi9CaDdVNTl1M2FVNTNrbkt5WlJ2Q3Y3eEJkdDJqcThRVkhZdUZLSTQKbXlFMGRLMWlkMkl0eWUyV2MzSVdob0tMUlZjTVprOUFxS1B2NGJ0Y1k3T3JaeEZkK1k3SzBYM1FBSUNMWUwxQQpSTGVaY2ZwTzlrRG1RUTFXYnZoNWFySm85M1RENml6aVIybjhEK3RqSzN6M3pTUFNZSEIwbEhSTFVyOEdJUjBNCi9GOFZBcDRjSVRsSkdIQVp6aEpmWE50bmNUaUZDNGNKblM5cVg3dzR0anpKMUF3ckg3K3JPVXBGTmZWR1NuWWoKeHdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t";
const base64EnclavePublicKey =
  "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUEydFoydkVpUmJKWVA2NC9xdkZSRQpOTWY1MUg3b3hXaWI2NHlQVW5JN3ZjemsyajY3aWFxREJYdGZLem9tTDc0bFM2Z3N0ZDRibGM0bU5hVGU1b0s3Cms1REM4aGlzWDRGM0J4YStuY3dweUpLTk5tZGxDTFBvNzdGUVczb3VnTndNS0VBQmhDbHIzZDdoQklESTN5VCsKOW0xa2xzNUxoOVdRUGlpVm5FSEE2b1VJRGlZZ0IwY2prU1hmWGpOUG9BNjdEWTRvV0dYMDRRZGZML2ZwUW1YVAp4ZGZ4cXRlS3p6ZXV0dE04OThMbVcySzhNNWtyOTJDZkVTTXJ1RnYvNUN6andwUWI1TXZiWDVSazBuRnJaVXpMCkUzS0VaZTJENCtaYU44dlQrek1OL2NPYnIvZFlHb1VZeWgzbEhLKzBHTmtqNWZiQWx1N3dBcjBOVzEzWFJ4SWkKMlFJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t";

const enclavePublicKey = Buffer.from(
  base64EnclavePublicKey,
  "base64url"
).toString("utf-8");

const aes_key = crypto.randomBytes(32);
const aes_iv = crypto.randomBytes(16);
const cipher_aes = crypto.createCipheriv("aes-256-cbc", aes_key, aes_iv);

const inputs_AESciphered = Buffer.concat([
  cipher_aes.update(Buffer.from(inputs, "utf8")),
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
  `script=${script}&inputs=${inputs_AESciphered}&key=${aes_key_RSAciphered}&iv=${aes_iv.toString(
    "base64url"
  )}`
);
