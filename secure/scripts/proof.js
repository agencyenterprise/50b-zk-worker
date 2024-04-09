import { plonk } from "snarkjs";

const zkey = process.argv[2];
const witness = process.argv[3];

const zkey_b = Uint8Array.from(Buffer.from(zkey, "base64url"));
const witness_b = Uint8Array.from(Buffer.from(witness, "base64url"));

const snarkjsProof = await plonk.prove(zkey_b, witness_b);

console.log(Buffer.from(JSON.stringify(snarkjsProof)).toString("base64url"));
process.exit();
