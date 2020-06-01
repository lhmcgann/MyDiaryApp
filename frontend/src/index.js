import "./custom.scss";
import React from "react";
import { BrowserRouter} from "react-router-dom";
import App from "./App";
import "./index.css";
import { render } from 'react-dom'

render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
  document.querySelector('#root')
)
