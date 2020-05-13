import React, { Component } from "react";
import { Link } from "react-router-dom";
const DiaryListBody = (props) => {
  const rows = props.characterData.map((row, index) => {
    return (
      <tr key={index}>
        <td>
          <div class="centered">
            <Link to="/diary/${id}">
              <button class="button1">{row.name}</button>
            </Link>
          </div>
        </td>
      </tr>
    );
  });

  return <tbody>{rows}</tbody>;
};
const DiaryList = (props) => {
  const { characterData } = props;

  return (
    <table>
      <DiaryListBody characterData={characterData} />
    </table>
  );
};
export default DiaryList;
