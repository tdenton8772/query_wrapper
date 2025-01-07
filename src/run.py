from application import create_app

# Create the application instance using the factory
application = create_app()

# Run the application
if __name__ in ('__main__', '__run__', 'run'):
    application.run(host='0.0.0.0', port=5000, debug=True)