import json
import hashlib
import datetime

# block class
class Block:
    def __init__(self, index, evidence_id, action, file_hash, from_person, to_person, previous_hash):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.evidence_id = evidence_id
        self.action = action
        self.file_hash = file_hash
        self.from_person = from_person
        self.to_person = to_person
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = (
            str(self.index)
            + self.timestamp
            + self.evidence_id
            + str(self.action)
            + str(self.file_hash)
            + str(self.from_person)
            + str(self.to_person)
            + self.previous_hash
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "evidence_id": self.evidence_id,
            "action": self.action,
            "file_hash": self.file_hash,
            "from_person": self.from_person,
            "to_person": self.to_person,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(data):
        block = Block(
            data["index"],
            data["evidence_id"],
            data["action"],
            data["file_hash"],
            data["from_person"],
            data["to_person"],
            data["previous_hash"]
        )
        block.timestamp = data["timestamp"]
        block.hash = data["hash"]
        return block

# blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []

    def create_genesis_block(self):
        return Block(0, "GENESIS", "GENESIS", "0", "SYSTEM", "SYSTEM", "0")

    def add_block(self, evidence_id, action, file_hash, from_person, to_person):
        previous_block = self.chain[-1]

        new_block = Block(
            len(self.chain),
            evidence_id,
            action,
            file_hash,
            from_person,
            to_person,
            previous_block.hash
        )

        self.chain.append(new_block)

    def save_to_file(self):
        with open("blockchain.json", "w") as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=4)

    def load_from_file(self):
        try:
            with open("blockchain.json", "r") as f:
                data = json.load(f)
                self.chain = [Block.from_dict(block) for block in data]
        except FileNotFoundError:
            self.chain = [self.create_genesis_block()]

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True

# hash function
def generate_file_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()

# display
def display_blockchain(blockchain):
    print("\n" + "="*50)
    print("        BLOCKCHAIN LEDGER")
    print("="*50)

    for block in blockchain.chain:
        print("\n" + "="*20 + f" BLOCK {block.index} " + "="*20)

        print(f"Timestamp     : {block.timestamp}")
        print(f"Evidence ID   : {block.evidence_id}")
        print(f"Action        : {block.action}")
        print(f"File Hash     : {block.file_hash}")
        print(f"From          : {block.from_person}")
        print(f"To            : {block.to_person}")
        print(f"Previous Hash : {block.previous_hash}")
        print(f"Current Hash  : {block.hash}")

        print("="*50)

# search id
def search_evidence(blockchain, evidence_id):
    found = False

    print("\n" + "="*50)
    print("        SEARCH RESULT")
    print("="*50)

    for block in blockchain.chain:
        if block.evidence_id == evidence_id:
            found = True
            print(f"\nBlock {block.index}")
            print(f"Action : {block.action}")
            print(f"From   : {block.from_person}")
            print(f"To     : {block.to_person}")

    if not found:
        print("No records found.")

# chain of custody
def show_chain_of_custody(blockchain, evidence_id):
    chain = []

    for block in blockchain.chain:
        if block.evidence_id == evidence_id:
            if block.action == "ADD":
                chain.append(block.to_person)
            elif block.action == "TRANSFER":
                chain.append(block.to_person)

    print("\n" + "="*50)
    print("      CHAIN OF CUSTODY")
    print("="*50)

    if chain:
        print(" → ".join(chain))
    else:
        print("No custody records found.")

# main
def main():
    blockchain = Blockchain()
    blockchain.load_from_file()

    while True:
        print("\n" + "="*50)
        print("   DIGITAL FORENSIC EVIDENCE TRACKER")
        print("="*50)

        print("1. Add Evidence")
        print("2. Transfer Evidence")
        print("3. Verify Evidence")
        print("4. View Blockchain")
        print("5. Validate Blockchain")
        print("6. Search Evidence")
        print("7. Show Chain of Custody")
        print("8. Exit")

        choice = input("Enter choice: ")

        # ADD EVIDENCE
        if choice == "1":
            evidence_id = input("Enter Evidence ID: ")
            file_path = input("Enter File Path: ")
            investigator = input("Enter Investigator Name: ")

            try:
                file_hash = generate_file_hash(file_path)

                # Duplicate check
                exists = False
                for block in blockchain.chain:
                    if block.evidence_id == evidence_id:
                        exists = True
                        break

                if exists:
                    print("\nEvidence ID already exists!")
                else:
                    blockchain.add_block(
                        evidence_id,
                        "ADD",
                        file_hash,
                        "SYSTEM",
                        investigator
                    )

                    blockchain.save_to_file()

                    print("\nEvidence added successfully!")
                    print("🔐File Hash:", file_hash)

            except FileNotFoundError:
                print("File not found!")

        # TRANSFER
        elif choice == "2":
            evidence_id = input("Enter Evidence ID: ")
            from_person = input("Transfer From: ")
            to_person = input("Transfer To: ")

            blockchain.add_block(
                evidence_id,
                "TRANSFER",
                "N/A",
                from_person,
                to_person
            )

            blockchain.save_to_file()

            print("\nEvidence transfer recorded successfully!")

        # VERIFY
        elif choice == "3":
            evidence_id = input("Enter Evidence ID: ")
            file_path = input("Enter File Path: ")

            try:
                new_hash = generate_file_hash(file_path)

                original_hash = None
                for block in blockchain.chain:
                    if block.evidence_id == evidence_id and block.file_hash != "N/A":
                        original_hash = block.file_hash
                        break

                print("\n" + "="*50)
                print("        EVIDENCE VERIFICATION")
                print("="*50)

                print(f"Stored Hash : {original_hash}")
                print(f"New Hash    : {new_hash}")

                if original_hash == new_hash:
                    print("\nIntegrity Verified")
                else:
                    print("\nWARNING: Evidence Tampered!")

            except FileNotFoundError:
                print("File not found!")

        # VIEW
        elif choice == "4":
            display_blockchain(blockchain)

        # VALIDATE
        elif choice == "5":
            print("\n" + "="*50)
            print("BLOCKCHAIN VALIDATION RESULT")
            print("="*50)

            if blockchain.validate_chain():
                print("Blockchain integrity verified")
            else:
                print("Blockchain tampered!")

        # SEARCH
        elif choice == "6":
            evidence_id = input("Enter Evidence ID: ")
            search_evidence(blockchain, evidence_id)

        # CHAIN OF CUSTODY
        elif choice == "7":
            evidence_id = input("Enter Evidence ID: ")
            show_chain_of_custody(blockchain, evidence_id)

        # EXIT
        elif choice == "8":
            print("Exiting program.")
            break

        else:
            print("Invalid choice.")

# run code
if __name__ == "__main__":
    main()