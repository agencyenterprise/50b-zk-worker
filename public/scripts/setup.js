import { plonk } from "snarkjs";

const r1csName = process.argv[2];
const zkeyName = `${r1csName}.zkey`;

await plonk.setup(r1csName, "scripts/powersOfTau15_final.ptau", zkeyName);

console.log(zkeyName);
process.exit();
