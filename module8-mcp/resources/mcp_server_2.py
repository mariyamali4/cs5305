from fastmcp import FastMCP
import random

# 1. Initialize the server
mcp = FastMCP("DemoSchoolServer")

# 2. Define a TOOL (An action the AI can take)
@mcp.tool()
def calculate_hypotenuse(a: float, b: float) -> float:
    """Calculates the hypotenuse of a right triangle given sides a and b."""
    return (a**2 + b**2)**0.5

# 3. Define a RESOURCE (Data the AI can read)
@mcp.resource("weather://local")
def get_local_weather() -> str:
    """Provides the current 'live' weather for the school campus."""
    temp = random.randint(15, 30)
    conditions = ["Sunny", "Cloudy", "Raining", "Windy"]
    return f"The current campus weather is {temp}°C and {random.choice(conditions)}."

if __name__ == "__main__":
    mcp.run()