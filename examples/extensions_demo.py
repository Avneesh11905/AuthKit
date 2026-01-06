from authkit.core import Registry
from authkit import AuthKit , UserRepository

class MyGreeter:
        def greet(self, name):
            print(f"Hello, {name}!")

@Registry.register("greet_user")
class GreetUserUseCase:
    # Use a CUSTOM dependency name to demonstrate injection
    def __init__(self, greeter: MyGreeter):
        self.greeter = greeter

    def execute(self, name: str):
        self.greeter.greet(name)

# 4. Define a Typed Facade for IDE Support (Optional but Recommended)
class MyAuthKit(AuthKit):
    """My custom AuthKit with extra features"""
    greet_user: GreetUserUseCase

def run():
    # 1. Initialize using the Typed Subclass
    class DummyRepo: pass
    
    # We define the custom service
    

    auth = MyAuthKit(
        user_repo=DummyRepo(),
    )
    
    # 2. Inject custom dependency via configure()
    # matches 'greeter' arg in GreetUserUseCase
    auth.configure(greeter=MyGreeter()) 
    
    # 3. Use the new use case
    # IDE knows about 'greet_user' because of MyAuthKit class!
    if hasattr(auth, "greet_user"):
        print("SUCCESS: auth.greet_user exists!")
        auth.greet_user.execute("World")
    else:
        print("FAILURE: auth.greet_user NOT found.")

if __name__ == "__main__":
    run()
