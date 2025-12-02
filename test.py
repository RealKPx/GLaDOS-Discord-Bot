import discord
print(discord.__file__)
print(discord.__version__ if hasattr(discord, "__version__") else "no version")
