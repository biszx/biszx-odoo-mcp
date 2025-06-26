"""
Tests for odoo_mcp_server.__main__ module
"""

from unittest.mock import patch

from odoo_mcp_server.__main__ import init, main
from odoo_mcp_server.exceptions import OdooMCPError


class TestInit:
    """Test cases for init function"""

    @patch("odoo_mcp_server.__main__.logger")
    def test_init_without_dotenv(self, mock_logger):
        """Test init function when dotenv is not available"""

        def mock_import(name, *args, **kwargs):
            if name == "dotenv":
                raise ImportError()
            return __import__(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Should not raise an exception
            init()

            # Logger should be configured
            mock_logger.remove.assert_called_once()
            mock_logger.add.assert_called_once()

    @patch("odoo_mcp_server.__main__.logger")
    def test_init_with_dotenv(self, mock_logger):
        """Test init function when dotenv is available"""
        with patch("dotenv.load_dotenv") as mock_load_dotenv:
            init()

            # dotenv should be loaded
            mock_load_dotenv.assert_called_once()

            # Logger should be configured
            mock_logger.remove.assert_called_once()
            mock_logger.add.assert_called_once()

    @patch.dict("os.environ", {"LOG_LEVEL": "DEBUG"})
    @patch("odoo_mcp_server.__main__.logger")
    def test_init_custom_log_level(self, mock_logger):
        """Test init function with custom log level"""
        init()

        # Verify logger.add was called with DEBUG level
        mock_logger.add.assert_called_once()
        call_args = mock_logger.add.call_args
        assert call_args[1]["level"] == "DEBUG"

    @patch("dotenv.load_dotenv")  # Prevent loading .env file
    @patch("odoo_mcp_server.__main__.logger")
    def test_init_default_log_level(self, mock_logger, mock_load_dotenv):
        """Test init function with default log level"""
        # Ensure LOG_LEVEL is not set in environment
        with patch.dict("os.environ", {}, clear=True):
            init()

            # Verify logger.add was called with INFO level (default)
            mock_logger.add.assert_called_once()
            call_args = mock_logger.add.call_args
            assert call_args[1]["level"] == "INFO"


class TestMain:
    """Test cases for main function"""

    @patch("odoo_mcp_server.__main__.mcp")
    @patch("odoo_mcp_server.__main__.logger")
    @patch("odoo_mcp_server.__main__.init")
    def test_main_success(self, mock_init, mock_logger, mock_mcp):
        """Test successful main execution"""
        # Mock successful MCP run
        mock_mcp.run.return_value = None

        result = main()

        # Verify initialization was called
        mock_init.assert_called_once()

        # Verify MCP server was started
        mock_mcp.run.assert_called_once()

        # Verify logging
        assert any(
            "starting" in str(call).lower() for call in mock_logger.info.call_args_list
        )
        assert any(
            "stopped" in str(call).lower() for call in mock_logger.info.call_args_list
        )

        # Should return 0 for success
        assert result == 0  # Intentionally checking exact value, not truthiness

    @patch("odoo_mcp_server.__main__.mcp")
    @patch("odoo_mcp_server.__main__.logger")
    @patch("odoo_mcp_server.__main__.init")
    def test_main_keyboard_interrupt(self, mock_init, mock_logger, mock_mcp):
        """Test main function with keyboard interrupt"""
        # Mock KeyboardInterrupt during MCP run
        mock_mcp.run.side_effect = KeyboardInterrupt()

        result = main()

        # Verify initialization was called
        mock_init.assert_called_once()

        # Verify keyboard interrupt was handled
        assert any(
            "stopped by user" in str(call).lower()
            for call in mock_logger.info.call_args_list
        )

        # Should return 0 for graceful shutdown
        assert result == 0  # Intentionally checking exact value, not truthiness

    @patch("odoo_mcp_server.__main__.mcp")
    @patch("odoo_mcp_server.__main__.logger")
    @patch("odoo_mcp_server.__main__.init")
    def test_main_odoo_mcp_error(self, mock_init, mock_logger, mock_mcp):
        """Test main function with OdooMCPError"""
        # Create a mock OdooMCPError
        error = OdooMCPError(
            "Test error", error_code="TEST_ERROR", details={"key": "value"}
        )
        mock_mcp.run.side_effect = error

        result = main()

        # Verify initialization was called
        mock_init.assert_called_once()

        # Verify error was logged
        assert any(
            "Odoo MCP Error" in str(call) for call in mock_logger.error.call_args_list
        )
        assert any(
            "Error details" in str(call) for call in mock_logger.debug.call_args_list
        )
        assert any(
            "Additional details" in str(call)
            for call in mock_logger.debug.call_args_list
        )

        # Should return 1 for error
        assert result == 1

    @patch("odoo_mcp_server.__main__.mcp")
    @patch("odoo_mcp_server.__main__.logger")
    @patch("odoo_mcp_server.__main__.init")
    def test_main_generic_exception(self, mock_init, mock_logger, mock_mcp):
        """Test main function with generic exception"""
        # Mock generic exception during MCP run
        error = ValueError("Test generic error")
        mock_mcp.run.side_effect = error

        result = main()

        # Verify initialization was called
        mock_init.assert_called_once()

        # Verify error was logged
        assert any(
            "Critical server error" in str(call)
            for call in mock_logger.error.call_args_list
        )
        assert any(
            "Exception type" in str(call) for call in mock_logger.debug.call_args_list
        )
        assert any(
            "Traceback" in str(call) for call in mock_logger.debug.call_args_list
        )

        # Should return 1 for error
        assert result == 1

    @patch("odoo_mcp_server.__main__.logger")
    def test_main_python_version_logging(self, mock_logger):
        """Test that Python version is logged"""
        with patch("odoo_mcp_server.__main__.mcp") as mock_mcp:
            mock_mcp.run.return_value = None

            main()

            # Verify Python version was logged
            assert any(
                "Python version" in str(call)
                for call in mock_logger.debug.call_args_list
            )

    @patch("odoo_mcp_server.__main__.logger")
    def test_main_mcp_initialization_logging(self, mock_logger):
        """Test that MCP initialization is logged"""
        with patch("odoo_mcp_server.__main__.mcp") as mock_mcp:
            mock_mcp.run.return_value = None

            main()

            # Verify MCP initialization was logged
            assert any(
                "MCP server initialized" in str(call)
                for call in mock_logger.debug.call_args_list
            )


class TestMainModule:
    """Test cases for module-level functionality"""

    def test_main_module_import(self):
        """Test that the main module can be imported"""
        import odoo_mcp_server.__main__

        assert hasattr(odoo_mcp_server.__main__, "main")
        assert hasattr(odoo_mcp_server.__main__, "init")
        assert callable(odoo_mcp_server.__main__.main)
        assert callable(odoo_mcp_server.__main__.init)

    @patch("odoo_mcp_server.__main__.main")
    @patch("sys.exit")
    def test_main_module_execution(self, mock_sys_exit, mock_main):
        """Test module execution when run as __main__"""
        mock_main.return_value = 0

        # Simulate running as main module
        with patch("odoo_mcp_server.__main__.__name__", "__main__"):
            # Import and execute the module
            exec(  # pylint: disable=exec-used
                compile(
                    # pylint: disable-next=consider-using-with
                    open("src/odoo_mcp_server/__main__.py", encoding="utf-8").read(),
                    "src/odoo_mcp_server/__main__.py",
                    "exec",
                )
            )

        # Note: This test is somewhat limited because we can't easily
        # test the actual if __name__ == "__main__" block without
        # more complex mocking

    def test_docstring_and_module_structure(self):
        """Test module docstring and basic structure"""
        import odoo_mcp_server.__main__ as main_module

        # Verify module has a docstring
        assert main_module.__doc__ is not None
        assert "Command line entry point" in main_module.__doc__

        # Verify required functions exist
        assert hasattr(main_module, "init")
        assert hasattr(main_module, "main")

        # Verify imports exist
        assert hasattr(main_module, "logger")
        assert hasattr(main_module, "mcp")


class TestIntegration:
    """Integration test cases"""

    @patch("odoo_mcp_server.__main__.mcp")
    @patch("odoo_mcp_server.__main__.logger")
    def test_full_execution_flow(self, mock_logger, mock_mcp):
        """Test the full execution flow"""
        mock_mcp.run.return_value = None

        # Test the complete flow
        result = main()

        # Verify the expected sequence of calls
        # 1. Logger should be configured
        mock_logger.remove.assert_called()
        mock_logger.add.assert_called()

        # 2. Startup messages should be logged
        startup_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("starting" in call.lower() for call in startup_calls)

        # 3. Debug information should be logged
        debug_calls = [str(call) for call in mock_logger.debug.call_args_list]
        assert any("python version" in call.lower() for call in debug_calls)

        # 4. MCP should be started
        mock_mcp.run.assert_called_once()

        # 5. Success should be logged
        assert any("stopped" in call.lower() for call in startup_calls)

        # 6. Should return success code
        assert result == 0
