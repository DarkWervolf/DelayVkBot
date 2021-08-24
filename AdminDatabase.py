import os.path

class AdminDatabase:
    def __init__(self):
        self.admins_id = []
        if os.path.exists("admins_id.txt"):
            self.load("admins_id.txt")

    def get_database(self):
        return self.admins_id

    def add(self, new_admin: int):
        self.admins_id.append(new_admin)
        self.save("admins_id.txt")

    def delete(self, admin_id: int):
        self.admins_id.remove(admin_id)
        self.save("admins_id.txt")

    def save(self, filename: str):
        output = ''
        for a in self.admins_id:
            output += str(a) + '\n'
        with open(filename, 'w') as f:
            f.write(output)

    def load(self, filename: str):
        with open(filename, 'r') as f:
            for line in f:
                self.admins_id.append(int(line))