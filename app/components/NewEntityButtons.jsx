import React, { useState } from 'react';
import { getEntityTypeIcon } from './utils';

export default function NewEntityButtons({ newCommentFunc, newStepFunc, newTaskFunc, newProjectFunc}) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className={`new-entity-buttons ${isHovered ? 'hovered' : ''}`}
      onMouseEnter={() => setIsHovered(true)} 
      onMouseLeave={() => setIsHovered(false)}
    >
      <button className="placeholder-button" title="Hover for addition options"> 
        <i className="bi-plus-circle placeholder"/>
      </button>
      {isHovered && (
        <div className={`extra-buttons ${isHovered ? 'hovered' : ''}`}>
          {newProjectFunc && (
            <button className="btn" title="Add a new Project to this entity" onClick={() => {newProjectFunc()}}>
              <span className="icon-with-plus">
                <i className={getEntityTypeIcon("Project")}/>
                <i className="bi bi-plus small-plus"/>
              </span>
            </button>
          )}
          {newTaskFunc && (
            <button className="btn" title="Add a new Task to this entity" onClick={() => {newTaskFunc()}}>
              <span className="icon-with-plus">
                <i className={getEntityTypeIcon("Task")}/>
                <i className="bi bi-plus small-plus"/>
              </span>
            </button>
          )}
          {newStepFunc && (
            <button className="btn" title="Add a new Step to this entity" onClick={() => {newStepFunc()}}>
              <span className="icon-with-plus">
                <i className={getEntityTypeIcon("Step")}/>
                <i className="bi bi-plus small-plus"/>
              </span>
            </button>
          )}
          {newCommentFunc && (
            <button className="btn" title="Add a new Comment to this entity" onClick={() => {newCommentFunc()}}>
              <span className="icon-with-plus">
                <i className="bi bi-chat-left-text"/>
                <i className="bi bi-plus small-plus"/>
              </span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};